# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestHrExpensePettyCash(common.TransactionCase):
    def setUp(self):
        super(TestHrExpensePettyCash, self).setUp()

        # Create an employee
        self.employee_id = self.env.ref('hr.employee_admin')

        # Create a product
        self.product_id = self.env.ref('hr_expense.air_ticket')

        # Create a Petty Cash Account
        liquidity_type = self.env.ref('account.data_account_type_liquidity')
        self.petty_cash_account_id = self.env['account.account'].create({
            'code': '000000',
            'name': 'Petty Cash - Test',
            'user_type_id': liquidity_type.id,
        })

        # Create Partner
        self.partner_1 = self.env['res.partner'].create({
            'name': 'Petty Cash Holder 1 - Test',
        })
        self.partner_2 = self.env['res.partner'].create({
            'name': 'Petty Cash Holder 2 - Test',
        })

    def create_petty_cash_holder(self, partner, petty_cash_balance=False):
        # Create a Petty Cash Holder
        petty_cash_holder = self.env['petty.cash'].create({
            'partner_id': partner.id,
            'account_id': self.petty_cash_account_id.id,
            'petty_cash_limit': 1000.00,
            'petty_cash_balance': petty_cash_balance or 0.0,
        })
        return petty_cash_holder

    def test_onchange_is_petty_cash(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)

        invoice = self.env['account.invoice'].create({
            'account_id': self.petty_cash_account_id.id,
            'type': 'out_invoice',
        })

        # Case 1: check Petty Cash without partner
        invoice.is_petty_cash = True
        with self.assertRaises(ValidationError):
            invoice._onchange_is_petty_cash()
            invoice._check_petty_cash_amount()
        self.assertEqual(
            len(invoice.invoice_line_ids), 0)

        invoice.is_petty_cash = False

        # Case 2: select partner not petty cash holder > check Petty Cash
        invoice.partner_id = self.partner_2.id
        invoice.is_petty_cash = True
        with self.assertRaises(ValidationError):
            invoice._onchange_is_petty_cash()
            invoice._check_petty_cash_amount()
        self.assertEqual(
            len(invoice.invoice_line_ids), 0)

        invoice.is_petty_cash = False

        # Case 3: select petty cash holder > check Petty Cash
        invoice.partner_id = self.partner_1.id
        product = self.env.ref('product.product_product_4')
        account = self.env.ref('account.data_account_type_revenue')
        self.env['account.invoice.line'].create({
            'product_id': product.id,
            'quantity': 1.000,
            'price_unit': 100.00,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': account.id,
        })
        invoice.is_petty_cash = True
        invoice._onchange_is_petty_cash()
        invoice.invoice_line_ids += invoice._add_petty_cash_invoice_line(
            petty_cash_holder)
        invoice._check_petty_cash_amount()
        invoice.action_invoice_open()
        self.assertEqual(len(invoice.invoice_line_ids), 1)

    def test_petty_cash(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)

        # Test Amount > Max Limit - Balance
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_1.id,
            'account_id': self.petty_cash_account_id.id,
            'type': 'out_invoice',
            'is_petty_cash': True,
        })
        self.env['account.invoice.line'].create({
            'name': 'Petty Cash',
            'account_id': self.petty_cash_account_id.id,
            'invoice_id': invoice.id,
            'quantity': 1.000,
            'price_unit': 2000.00,
        })
        self.assertEqual(len(invoice.invoice_line_ids), 1)
        with self.assertRaises(ValidationError):
            invoice._check_petty_cash_amount()

    def test_expense(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)

        expense_report = self.env['hr.expense.sheet'].create({
            'name': 'Expense Report - Test',
            'employee_id': self.employee_id.id,
        })
        expense = self.env['hr.expense'].create({
            'name': 'Expense - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 500.00,
            'sheet_id': expense_report.id,
            'payment_mode': 'petty_cash',
            'petty_cash_id': petty_cash_holder.id,
        })
        expense._onchange_product_id()

        with self.assertRaises(ValidationError):
            expense_report._check_petty_cash_amount()

        # Submitted to Manager
        expense_report.action_submit_sheet()
        self.assertEquals(expense_report.state, 'submit')
        with self.assertRaises(ValidationError):
            expense_report._check_petty_cash_amount()
        # Approve
        expense_report.approve_expense_sheets()
        self.assertEquals(expense_report.state, 'approve')
        with self.assertRaises(ValidationError):
            expense_report._check_petty_cash_amount()
        # Create Expense Entries
        expense_report.action_sheet_move_create()
        self.assertEquals(expense_report.state, 'done')
        self.assertTrue(
            expense_report.account_move_id.id, 'Expense Entry is not created')

    def test_a_expense(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)

        expense_report = self.env['hr.expense.sheet'].create({
            'name': 'Expense Report - Test',
            'employee_id': self.employee_id.id,
        })
        expense = self.env['hr.expense'].create({
            'name': 'Expense - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 500.00,
            'sheet_id': expense_report.id,
            'payment_mode': 'petty_cash',
            'petty_cash_id': petty_cash_holder.id,
        })
        expense._onchange_product_id()

        # Submitted to Manager
        expense_report.action_submit_sheet()
        self.assertEquals(expense_report.state, 'submit')

        # Approve
        expense_report.approve_expense_sheets()
        self.assertEquals(expense_report.state, 'approve')

        # Create Expense Entries
        expense_report.action_sheet_move_create()
        self.assertEquals(expense_report.state, 'done')
        self.assertTrue(
            expense_report.account_move_id.id, 'Expense Entry is not created')

    def test_multiexpense(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1, 1000)

        expense_1 = self.env['hr.expense'].create({
            'name': 'Expense 1 - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 500.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': petty_cash_holder.id,
        })
        expense_1._onchange_product_id()
        expense_2 = self.env['hr.expense'].create({
            'name': 'Expense 2 - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 500.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': petty_cash_holder.id,
        })
        expense_2._onchange_product_id()
        expense = self.env['hr.expense'].search([('id', 'in', (
            expense_1.id, expense_2.id))])
        expense.action_submit_expenses()

    def test_multiexpense_multipettycashholder(self):
        pc_holder_1 = self.create_petty_cash_holder(self.partner_1, 1000)
        pc_holder_2 = self.create_petty_cash_holder(self.partner_2, 1000)
        expense_1 = self.env['hr.expense'].create({
            'name': 'Expense 1 - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 700.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': pc_holder_1.id,
        })
        expense_1._onchange_product_id()
        expense_2 = self.env['hr.expense'].create({
            'name': 'Expense 2 - Test',
            'employee_id': self.employee_id.id,
            'product_id': self.product_id.id,
            'unit_amount': 700.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': pc_holder_2.id,
        })
        expense_2._onchange_product_id()
        expenses = self.env['hr.expense'].search([(
            'id', 'in', (expense_1.id, expense_2.id))])
        with self.assertRaises(ValidationError):
            expenses.action_submit_expenses()
