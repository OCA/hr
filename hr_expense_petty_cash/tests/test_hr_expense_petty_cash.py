# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestHrExpensePettyCash(common.TransactionCase):
    def setUp(self):
        super(TestHrExpensePettyCash, self).setUp()

        # Create an employee
        self.employee_id = self.env.ref('hr.employee_admin')

        # Create a product
        self.product_id = self.env.ref('hr_expense.air_ticket')

        # Create an account payable
        payable_type = self.env.ref('account.data_account_type_payable')
        self.account_id = self.env['account.account'].create({
            'code': '111111',
            'name': 'Payable - Test',
            'user_type_id': payable_type.id,
            'reconcile': True,
        })

        # Create a Petty Cash Account
        liquidity_type = self.env.ref('account.data_account_type_liquidity')
        self.petty_cash_account_id = self.env['account.account'].create({
            'code': '000000',
            'name': 'Petty Cash - Test',
            'user_type_id': liquidity_type.id,
        })

        # Create Partner
        self.partner_1 = self.env['res.partner'].create({
            'name': 'Partner 1 - Test',
        })
        self.partner_2 = self.env['res.partner'].create({
            'name': 'Partner 2 - Test',
        })

    def create_petty_cash_holder(self, partner, petty_cash_balance=False):
        petty_cash_holder = self.env['petty.cash'].create({
            'partner_id': partner.id,
            'account_id': self.petty_cash_account_id.id,
            'petty_cash_limit': 1000.00,
            'petty_cash_balance': petty_cash_balance or 0.0,
        })
        return petty_cash_holder

    def test_petty_cash(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_1.id,
            'account_id': self.account_id.id,
            'type': 'in_invoice',
            'is_petty_cash': True,
        })
        self.env['account.invoice.line'].create({
            'name': 'Petty Cash',
            'account_id': self.petty_cash_account_id.id,
            'invoice_id': invoice.id,
            'quantity': 1.000,
            'price_unit': 1000.00,
        })
        invoice.action_invoice_open()
        petty_cash_holder._compute_petty_cash_balance()
        self.assertEqual(petty_cash_holder.petty_cash_balance, 1000.00)

    def test_account_invoice_1(self):
        # Check Petty Cash without partner
        with self.assertRaises(ValidationError):
            invoice = self.env['account.invoice'].create({
                'account_id': self.account_id.id,
                'type': 'in_invoice',
                'is_petty_cash': True,
            })
            invoice._check_petty_cash_amount()
            invoice._onchange_is_petty_cash()

    def test_account_invoice_2(self):
        # Select partner not petty cash holder > check Petty Cash
        with self.assertRaises(ValidationError):
            invoice = self.env['account.invoice'].create({
                'partner_id': self.partner_1.id,
                'account_id': self.account_id.id,
                'type': 'in_invoice',
                'is_petty_cash': True,
            })
            invoice._check_petty_cash_amount()
            invoice._onchange_is_petty_cash()

    def test_account_invoice_3(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)
        product = self.env.ref('product.product_product_4')

        # Select petty cash holder > check Petty Cash
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_1.id,
            'account_id': self.account_id.id,
            'type': 'in_invoice',
            'is_petty_cash': True,
        })
        self.env['account.invoice.line'].create({
            'product_id': product.id,
            'quantity': 1.000,
            'price_unit': 300.00,
            'invoice_id': invoice.id,
            'name': 'something',
            'account_id': self.account_id.id,
        })
        invoice._check_petty_cash_amount()
        invoice._onchange_is_petty_cash()

    def test_account_invoice_4(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)

        # Test Amount > Max Limit - Balance
        invoice = self.env['account.invoice'].create({
            'partner_id': self.partner_1.id,
            'account_id': self.account_id.id,
            'type': 'in_invoice',
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
        invoice._onchange_is_petty_cash()

    def test_expense_sheet(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)
        self.assertEqual(petty_cash_holder.petty_cash_balance, 0.00)

        with self.assertRaises(ValidationError):
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

    def test_a_expense(self):
        petty_cash_holder = self.create_petty_cash_holder(self.partner_1)

        with self.assertRaises(ValidationError):
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
