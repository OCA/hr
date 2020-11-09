from odoo.exceptions import UserError
from odoo.tests import common


class TestHrExpense(common.TransactionCase):

    def setUp(self):
        super(TestHrExpense, self).setUp()

        self.product_expense = self.env['product.product'].create({
            'name': 'Flight Ticket',
            'standard_price': 700,
            'list_price': 700,
            'type': 'service',
            'default_code': 'CONSU-DELI-COST',
            'taxes_id': False,
            'expense_receipt_required': True
        })

    def test_flight_expense_submission_without_attachment(self):
        flight_expense = self.env['hr.expense'].create({
            'name': 'Flight Expense',
            'product_id': self.product_expense.id,
            'unit_amount': 100.0,
            'quantity': 1,
            'employee_id': self.env.ref('hr.employee_hne').id
        })
        with self.assertRaises(UserError):
            flight_expense.action_submit_expenses()

    def test_flight_expense_report_submission_without_attachment(self):
        expense = self.env['hr.expense.sheet'].create({
            'name': 'Expense for Abigail Peterson',
            'employee_id': self.env.ref('hr.employee_hne').id,
        })
        expense_line = self.env['hr.expense'].create({
            'name': 'Flight Expense',
            'employee_id': self.env.ref('hr.employee_hne').id,
            'product_id': self.product_expense.id,
            'unit_amount': 700.00,
            'quantity': 1,
            'sheet_id': expense.id,
        })
        expense_line._onchange_product_id()
        with self.assertRaises(UserError):
            expense.action_submit_sheet()
