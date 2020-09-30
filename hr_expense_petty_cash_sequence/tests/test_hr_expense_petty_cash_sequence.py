# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import SavepointCase


class TestHrExpenseSequence(SavepointCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
        self.account_model = self.env['account.account']
        self.move_model = self.env['account.move']
        self.move_line_model = self.env['account.move.line']
        self.journal_model = self.env['account.journal']
        self.expense_model = self.env['hr.expense']
        self.expense_sheet_model = self.env['hr.expense.sheet']
        self.product = self.env.ref('product.product_product_4')

        employee_home = self.env['res.partner'].create({
            'name': 'Employee Home Address',
        })
        self.employee = self.env['hr.employee'].create({
            'name': 'Employee',
            'address_home_id': employee_home.id,
        })
        self.account_payable_id = self.account_model.create({
            'code': '111111',
            'name': 'Payable - Test',
            'user_type_id': self.env.ref('account.data_account_type_payable').id,
            'reconcile': True,
        })
        self.petty_cash_account_id = self.account_model.create({
            'code': '000000',
            'name': 'Petty Cash - Test',
            'user_type_id': self.env.ref('account.data_account_type_liquidity').id,
        })
        self.petty_cash_holder = self.env['petty.cash'].create({
            'partner_id': employee_home.id,
            'account_id': self.petty_cash_account_id.id,
            'petty_cash_limit': 1000.00,
        })
        # Add Petty Cash Balance
        self.purchase_journal = self.journal_model.create({
            'name': 'purchase',
            'code': 'P',
            'type': 'purchase',
        })
        move = self.move_model.create({
            'name': 'purchase',
            'journal_id': self.purchase_journal.id,
            'line_ids': [
                (0, False, {
                    'credit': 1000.00,
                    'account_id': self.account_payable_id.id,
                    }),
                (0, False, {
                    'debit': 1000.00,
                    'account_id': self.petty_cash_account_id.id,
                    'name': 'Petty Cash',
                    'partner_id': employee_home.id,
                    }),
            ]
        })
        move.post()

    def test_create_sequence_from_expense(self):
        """ Returns an open expense """
        expense = self.env['hr.expense'].create({
            'name': 'Expense - Test',
            'employee_id': self.employee.id,
            'product_id': self.product.id,
            'unit_amount': 500.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': self.petty_cash_holder.id,
        })
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Expense Report - Test',
            'employee_id': self.employee.id,
            'payment_mode': 'petty_cash',
            'petty_cash_id': self.petty_cash_holder.id,
            'expense_line_ids': [[4, expense.id, False]],
        })
        self.assertNotEqual(expense_sheet.number, '/', 'Number create')

    def test_create_sequence_from_report(self):
        # Test number != '/'
        expense = self.env['hr.expense'].create({
            'name': 'Expense - Test',
            'employee_id': self.employee.id,
            'product_id': self.product.id,
            'unit_amount': 500.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': self.petty_cash_holder.id,
        })
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Expense Report - Test',
            'employee_id': self.employee.id,
            'payment_mode': 'petty_cash',
            'petty_cash_id': self.petty_cash_holder.id,
            'expense_line_ids': [(6, 0, [expense.id])],
        })
        self.assertNotEqual(expense_sheet.number, '/', 'Number create')
        # Test number 1 != number 2
        expense2 = self.env['hr.expense'].create({
            'name': 'Expense - Test',
            'employee_id': self.employee.id,
            'product_id': self.product.id,
            'unit_amount': 500.00,
            'payment_mode': 'petty_cash',
            'petty_cash_id': self.petty_cash_holder.id,
        })
        expense_sheet2 = self.env['hr.expense.sheet'].create({
            'name': 'Expense Report - Test',
            'employee_id': self.employee.id,
            'payment_mode': 'petty_cash',
            'petty_cash_id': self.petty_cash_holder.id,
            'expense_line_ids': [(6, 0, [expense2.id])],
        })

        sheet_number_1 = expense_sheet.number
        sheet_number_2 = expense_sheet2.number
        self.assertNotEqual(
            sheet_number_1,
            sheet_number_2,
            'Numbers are different'
        )
