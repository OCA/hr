# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as common
from odoo.exceptions import UserError
from ..hooks import post_init_hook


class TestHrExpenseCancel(common.TransactionCase):

    def setUp(self):
        super(TestHrExpenseCancel, self).setUp()
        self.payment_obj = self.env['account.payment']
        self.payment_journal = self.env['account.journal'].search(
            [('type', 'in', ['cash', 'bank'])], limit=1)
        self.payment_journal.update_posted = True

        self.main_company = company = self.env.ref('base.main_company')
        self.expense_journal = self.env['account.journal'].create({
            'name': 'Purchase Journal - Test',
            'code': 'HRTPJ',
            'type': 'purchase',
            'company_id': company.id,
            'update_posted': True,
        })

        self.expense_sheet = self.env['hr.expense.sheet'].create({
            'employee_id': self.ref("hr.employee_admin"),
            'name': 'Expense test',
            'journal_id': self.expense_journal.id,
        })
        self.expense_sheet.approve_expense_sheets()

        self.expense = self.env['hr.expense'].create({
            'name': 'Expense test',
            'employee_id': self.ref("hr.employee_admin"),
            'product_id': self.ref('hr_expense.air_ticket'),
            'unit_amount': 1,
            'quantity': 10,
            'sheet_id': self.expense_sheet.id,
        })
        self.expense._onchange_product_id()

    def _get_payment_wizard(self):
        ctx = dict(active_ids=self.expense_sheet.ids)
        wizard_obj = self.env['hr.expense.sheet.register.payment.wizard']
        p_methods = self.payment_journal.outbound_payment_method_ids
        return wizard_obj.with_context(ctx).create({
            'journal_id': self.payment_journal.id,
            'amount': self.expense_sheet.total_amount,
            'payment_method_id': p_methods and p_methods[0].id or False,
            'payment_type': 'inbound',
        })

    def test_post_init_hook(self):
        self.expense_sheet.action_sheet_move_create()
        payment_wizard = self._get_payment_wizard()
        payment_wizard.expense_post_payment()

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)

        payment.expense_sheet_id = False

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertFalse(payment)

        post_init_hook(self.env.cr, self.registry)

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)

    def test_get_payment_vals(self):
        self.expense_sheet.action_sheet_move_create()

        payment_wizard = self._get_payment_wizard()

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertFalse(payment)

        payment_wizard.expense_post_payment()
        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)

    def test_action_sheet_move_create(self):
        self.expense.payment_mode = 'company_account'

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertFalse(payment)

        self.expense_sheet.action_sheet_move_create()
        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)

    def test_action_cancel_posted(self):
        self.expense_sheet.action_sheet_move_create()

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertFalse(len(payment), 1)
        self.assertTrue(self.expense_sheet.account_move_id)

        self.expense_sheet.action_cancel()
        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertFalse(payment)
        self.assertFalse(self.expense_sheet.account_move_id)

    def test_action_cancel_no_update_posted(self):
        journals = self.payment_journal | self.expense_journal
        journals.write({'update_posted': False})
        with self.assertRaises(UserError):
            self.test_action_cancel_company_account()
        with self.assertRaises(UserError):
            self.test_action_cancel_own_account()

    def test_action_cancel_company_account(self):
        self.expense.payment_mode = 'company_account'
        self.expense_sheet.action_sheet_move_create()

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)
        self.assertTrue(self.expense_sheet.account_move_id)

        self.expense_sheet.action_cancel()
        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertFalse(payment)
        self.assertFalse(self.expense_sheet.account_move_id)

    def test_action_cancel_own_account(self):
        self.expense_sheet.action_sheet_move_create()

        payment_wizard = self._get_payment_wizard()
        payment_wizard.expense_post_payment()

        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)
        self.assertTrue(self.expense_sheet.account_move_id)

        self.expense_sheet.action_cancel()
        payment = self.payment_obj.search(
            [('expense_sheet_id', '=', self.expense_sheet.id)])
        self.assertEqual(len(payment), 1)
        self.assertEqual(payment.state, 'cancelled')
        self.assertFalse(self.expense_sheet.account_move_id)
