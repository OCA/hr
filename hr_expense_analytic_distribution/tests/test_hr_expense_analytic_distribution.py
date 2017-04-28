# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>.
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests import common


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
        cls.expense = cls.env['hr.expense'].create({
            'employee_id': cls.env.ref('hr.employee_mit').id,
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
        # Expense is approved by admin
        self.expense.approve_expenses()
        # Post entries are created
        self.expense.action_move_create()
        for line in self.expense.account_move_id.line_ids:
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
