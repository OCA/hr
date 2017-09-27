# -*- coding: utf-8 -*-
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestHrExpenseInvoice(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrExpenseInvoice, cls).setUpClass()

        partner = cls.env['res.partner'].create({
            'name': 'Test partner',
            'supplier': True,
        })
        receivable = cls.env.ref('account.data_account_type_receivable').id
        expenses = cls.env.ref('account.data_account_type_expenses').id
        invoice_account = cls.env['account.account'].search(
            [('user_type_id', '=', receivable)], limit=1).id
        invoice_line_account = cls.env['account.account'].search(
            [('user_type_id', '=', expenses)], limit=1).id
        product = cls.env['product.product'].create({
            'name': 'Product test',
            'type': 'service',
        })
        cls.invoice = cls.env['account.invoice'].create({
            'partner_id': partner.id,
            'account_id': invoice_account,
            'type': 'in_invoice',
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'quantity': 1.0,
                'price_unit': 100.0,
                'name': 'product that cost 100',
                'account_id': invoice_line_account,
            })]
        })
        cls.sheet = cls.env['hr.expense.sheet'].create({
            'name': 'Test expense sheet',
        })
        cls.expense = cls.env['hr.expense'].create({
            'name': 'Expense test',
            'product_id': product.id,
            'unit_amount': 0.0,
        })

    def test_hr_test_invoice(self):
        # There is not expense lines in sheet
        self.assertEqual(len(self.sheet.expense_line_ids), 0)
        # We add an expense
        self.sheet.expense_line_ids = [(6, 0, [self.expense.id])]
        self.assertEqual(len(self.sheet.expense_line_ids), 1)
        # We add invoice to expense
        self.invoice.action_invoice_open()
        self.expense.invoice_id = self.invoice.id
        self.expense.onchange_invoice_id()
        self.assertAlmostEqual(self.expense.total_amount, 100.0)
        # We approve sheet
        self.sheet.approve_expense_sheets()
        self.assertEqual(self.sheet.state, 'approve')
        self.assertFalse(self.sheet.account_move_id)
        self.assertEqual(self.invoice.state, 'open')
        # We posrt journal entries
        self.sheet.action_sheet_move_create()
        self.assertEqual(self.sheet.state, 'post')
        self.assertTrue(self.sheet.account_move_id)
        # Invoice is now paid
        self.assertEqual(self.invoice.state, 'paid')
