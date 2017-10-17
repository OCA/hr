# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>.
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrExpenseAnalyticDistribution(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrExpenseAnalyticDistribution, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Test product',
        })
        cls.account1 = cls.env['account.analytic.account'].create({
            'name': 'account1',
        })
        cls.account2 = cls.env['account.analytic.account'].create({
            'name': 'account2',
        })
        cls.instance = cls.env['account.analytic.distribution'].create({
            'name': 'plan',
            'rule_ids': [
                (0, 0, {
                    'percent': 50.0,
                    'analytic_account_id': cls.account1.id,
                }),
                (0, 0, {
                    'percent': 50.0,
                    'analytic_account_id': cls.account2.id,
                }),
            ],
        })
        cls.sheet = cls.env['hr.expense.sheet'].create({
            'name': 'Test expense sheet',
        })
        cls.expense = cls.env['hr.expense'].create({
            'name': 'Test expense',
            'analytic_distribution_id': cls.instance.id,
            'product_id': cls.product.id,
            'product_uom_id':
                cls.env.ref('product.product_uom_unit').id,
            'unit_amount': 42,
            'quantity': 1,
        })

    def test_hr_expense_analytic_distribution(self):
        # Expense has been submitted
        self.expense.submit_expenses()
        # We add an expense to sheet
        self.sheet.expense_line_ids = [(6, 0, [self.expense.id])]
        self.assertEqual(len(self.sheet.expense_line_ids), 1)
        # Expense is approved
        self.sheet.approve_expense_sheets()
        # Post entries are created
        self.sheet.action_sheet_move_create()
        for line in self.sheet.account_move_id.line_ids:
            if line.analytic_line_ids:
                self.assertEqual(len(line.analytic_line_ids), 2)
                self.assertIn(self.account1, [
                    l.account_id for l in line.analytic_line_ids])
                self.assertIn(self.account2, [
                    l.account_id for l in line.analytic_line_ids])
                for l in line.analytic_line_ids:
                    if l.move_id.credit:
                        self.assertAlmostEqual(l.amount, 21)
                    if l.move_id.debit:
                        self.assertAlmostEqual(l.amount, -21)
