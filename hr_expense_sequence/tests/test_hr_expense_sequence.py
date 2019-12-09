# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestHrExpenseSequence(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestHrExpenseSequence, cls).setUpClass()
        cls.expense_model = cls.env["hr.expense"]
        cls.expense_sheet_model = cls.env["hr.expense.sheet"]
        cls.product = cls.env.ref("product.product_product_4")

        employee_home = cls.env["res.partner"].create({"name": "Employee Home Address"})
        cls.employee = cls.env["hr.employee"].create(
            {"name": "Employee", "address_home_id": employee_home.id}
        )
        cls.expense = cls.create_expense(cls, "Expense")

    def create_expense(self, name):
        """ Returns an open expense """
        expense = self.expense_model.create(
            {
                "name": name,
                "employee_id": self.employee.id,
                "product_id": self.product.id,
                "unit_amount": self.product.standard_price,
                "quantity": 1,
            }
        )
        expense.action_submit_expenses()
        return expense

    def test_create_sequence(self):
        # Test number != '/'
        self.sheet = self.expense_sheet_model.create(
            {"name": "Expense Report", "employee_id": self.employee.id}
        )
        self.assertNotEqual(self.sheet.number, "/", "Number create")
        # Test number 1 != number 2
        expense_number_1 = self.sheet.number
        expense2 = self.sheet.copy()
        expense_number_2 = expense2.number
        self.assertNotEqual(expense_number_1, expense_number_2, "Numbers are different")
