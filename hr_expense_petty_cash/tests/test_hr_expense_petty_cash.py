# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, Form


class TestHrExpensePettyCash(TransactionCase):
    def setUp(self):
        super(TestHrExpensePettyCash, self).setUp()

        self.employee_id = self.env.ref('hr.employee_admin')
        self.product_id = self.env.ref('hr_expense.air_ticket')
        self.partner_1 = self.env.ref('base.res_partner_1')
        self.partner_2 = self.env.ref('base.res_partner_2')
        self.payable_type = self.env.ref('account.data_account_type_payable')
        self.liquidity_type = \
            self.env.ref('account.data_account_type_liquidity')
        self.account_id = self.env['account.account'].create({
            'code': '111111',
            'name': 'Payable - Test',
            'user_type_id': self.payable_type.id,
            'reconcile': True,
        })
        self.petty_cash_journal_id = self.env['account.journal'].create({
            'code': 'PC',
            'name': 'Petty Cash',
            'type': 'general'
        })

        # Create a Petty Cash Account
        self.petty_cash_account_id = self.env['account.account'].create({
            'code': '000000',
            'name': 'Petty Cash - Test',
            'user_type_id': self.liquidity_type.id,
        })
        self.petty_cash_holder = self._create_petty_cash_holder(self.partner_1)

    def _create_petty_cash_holder(self, partner, petty_cash_balance=False):
        petty_cash_holder = self.env['petty.cash'].create({
            'partner_id': partner.id,
            'account_id': self.petty_cash_account_id.id,
            'petty_cash_limit': 1000.0,
            'petty_cash_balance': petty_cash_balance or 0.0,
        })
        return petty_cash_holder

    def _create_invoice(self, partner=False):
        invoice = self.env['account.invoice'].create({
            'partner_id': partner,
            'account_id': self.account_id.id,
            'type': 'in_invoice',
        })
        return invoice

    def _create_expense(self, amount, mode, petty_cash_holder=False):
        expense = self.env['hr.expense'].create({
            'name': 'Expense - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': amount,
            'payment_mode': mode,
            'petty_cash_id': petty_cash_holder,
        })
        return expense

    def _create_expense_sheet(self, expense):
        expense_sheet = self.env['hr.expense.sheet'].with_context(
            {'default_petty_cash_id': self.petty_cash_holder.id}
        ).create({
            'name': expense.name,
            'employee_id': expense.employee_id.id,
            'expense_line_ids': [(6, 0, [expense.id])],
        })
        return expense_sheet

    def test_01_create_petty_cash_holder(self):
        self.assertEqual(self.petty_cash_holder.petty_cash_balance, 0.00)
        # no partner and check petty cash
        invoice = self._create_invoice()
        with self.assertRaises(ValidationError):
            with Form(invoice) as inv:
                inv.is_petty_cash = True
        # partner is not holder.
        invoice = self._create_invoice(self.partner_2.id)
        with self.assertRaises(ValidationError):
            with Form(invoice) as inv:
                inv.is_petty_cash = True
        invoice = self._create_invoice(self.partner_1.id)
        with Form(invoice) as inv:
            inv.is_petty_cash = True
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        self.assertEqual(invoice.invoice_line_ids.price_unit, 1000.0)

        invoice.invoice_line_ids.price_unit = 1500.0
        with self.assertRaises(ValidationError):
            invoice._check_petty_cash_amount()

        invoice.invoice_line_ids.price_unit = 1000.0
        invoice.action_invoice_open()
        self.assertEqual(self.petty_cash_holder.petty_cash_balance, 1000.0)

    def test_02_create_expense_petty_cash(self):
        invoice = self._create_invoice(self.partner_1.id)
        with Form(invoice) as inv:
            inv.is_petty_cash = True
            inv.invoice_line_ids.price_unit = 1000.0
        invoice.action_invoice_open()
        self.assertEqual(self.petty_cash_holder.petty_cash_balance, 1000.0)
        # Create expense
        expense_own = self._create_expense(400.0, 'own_account')
        expense_petty_cash = self._create_expense(
            400.0, 'petty_cash', self.petty_cash_holder.id)
        expense_report = expense_own + expense_petty_cash
        with self.assertRaises(ValidationError):
            expense_report.action_submit_expenses()
        result = expense_petty_cash.action_submit_expenses()
        default_expense_line_ids = \
            result.get('context').get('default_expense_line_ids')
        sheet = self._create_expense_sheet(expense_petty_cash)
        self.assertEqual(sheet.expense_line_ids.ids, default_expense_line_ids)
        self.assertEqual(sheet.state, 'draft')
        with self.assertRaises(ValidationError):
            sheet.expense_line_ids.unit_amount = 1600.0
        sheet.expense_line_ids.unit_amount = 400.0
        # Submitted to Manager and Approve
        sheet.action_submit_sheet()
        self.assertEquals(sheet.state, 'submit')
        sheet.approve_expense_sheets()
        self.assertEquals(sheet.state, 'approve')
        # Create Expense Entries
        sheet.action_sheet_move_create()
        self.assertEquals(sheet.state, 'done')
        self.assertTrue(sheet.account_move_id.id)
        self.assertEquals(self.petty_cash_holder.petty_cash_balance, 600.0)

    def test_03_create_expense_petty_cash_with_journal(self):
        self.petty_cash_holder.journal_id = self.petty_cash_journal_id
        invoice = self._create_invoice(self.partner_1.id)
        with Form(invoice) as inv:
            inv.is_petty_cash = True
            inv.invoice_line_ids.price_unit = 1000.0
        self.assertEqual(invoice.journal_id, self.petty_cash_holder.journal_id)
        invoice.action_invoice_open()
        self.assertEqual(self.petty_cash_holder.petty_cash_balance, 1000.0)
        expense_petty_cash = self._create_expense(
            400.0, 'petty_cash', self.petty_cash_holder.id)
        sheet = self._create_expense_sheet(expense_petty_cash)
        self.assertEqual(sheet.journal_id, self.petty_cash_holder.journal_id)
