# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo.tests.common import Form, SavepointCase


class TestHrExpenseAdvanceClearingSequence(SavepointCase):

    @classmethod
    def setUpClass(self):
        super().setUpClass()
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
        advance_account = self.env['account.account'].create({
            'code': '154000',
            'name': 'Employee Advance',
            'user_type_id': self.env.ref(
                'account.data_account_type_current_assets').id,
            'reconcile': True,
        })
        self.emp_advance = self.env.ref('hr_expense_advance_clearing.'
                                        'product_emp_advance')
        self.emp_advance.property_account_expense_id = advance_account

        self.expense = self._create_expense(self, 'Advance 1,000', self.employee,
                                            self.emp_advance, 1000.0, advance=True)

        self.sheet = self._create_expense_sheet(
            self, 'Advance 1,000', self.employee, self.emp_advance, 1000.0,
            advance=True)

    def _create_expense(self, description, employee,
                        product, amount, advance=False,
                        payment_mode='own_account'):
        with Form(self.env['hr.expense']) as expense:
            expense.advance = advance
            expense.name = description
            expense.employee_id = employee
            expense.product_id = product
            expense.unit_amount = amount
            expense.payment_mode = payment_mode
        expense = expense.save()
        expense.tax_ids = False  # Test no vat
        return expense

    def _create_expense_sheet(self, description, employee,
                              product, amount, advance=False):
        expense = self._create_expense(self, description, employee,
                                       product, amount, advance)
        # Add expense to expense sheet
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': description,
            'employee_id': expense.employee_id.id,
            'expense_line_ids': [(6, 0, [expense.id])],
        })
        return expense_sheet

    def test_create_sequence_from_expense(self):
        # Test number != '/'
        expense_sheet = self.env['hr.expense.sheet'].create({
            'name': 'Advance 1,000',
            'employee_id': self.expense.employee_id.id,
            'expense_line_ids': [[4, self.expense.id, False]],
        })
        self.assertNotEqual(expense_sheet.number, '/', 'Number create')
        # Test number 1 != number 2
        sheet_number_1 = expense_sheet.number
        sheet2 = expense_sheet.copy()
        sheet_number_2 = sheet2.number
        self.assertNotEqual(
            sheet_number_1,
            sheet_number_2,
            'Numbers are different'
        )

    def test_create_sequence_from_report(self):
        # Test number != '/'
        self.assertNotEqual(self.sheet.number, '/', 'Number create')
        # Test number 1 != number 2
        sheet_number_1 = self.sheet.number
        sheet2 = self.sheet.copy()
        sheet_number_2 = sheet2.number
        self.assertNotEqual(
            sheet_number_1,
            sheet_number_2,
            'Numbers are different'
        )
