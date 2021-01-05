# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestHrContractRate(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.HrEmployee = self.env["hr.employee"]
        self.HrContract = self.env["hr.contract"]

    def test_compatibility(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "wage": 5000.0,
            }
        )

        self.assertEqual(contract.amount, 5000.0)
        self.assertEqual(contract.amount_period, "month")

    def test_hourly(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "amount": 50.0,
                "amount_period": "hour",
            }
        )

        self.assertEqual(contract.wage, 0.0)
        self.assertEqual(contract.approximate_wage, 8666.67)
        self.assertFalse(contract.is_wage_accurate)

    def test_daily(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "amount": 400.0,
                "amount_period": "day",
            }
        )

        self.assertEqual(contract.wage, 0.0)
        self.assertEqual(contract.approximate_wage, 8666.67)
        self.assertFalse(contract.is_wage_accurate)

    def test_weekly(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "amount": 2000.0,
                "amount_period": "week",
            }
        )

        self.assertEqual(contract.wage, 0.0)
        self.assertEqual(contract.approximate_wage, 8666.67)
        self.assertFalse(contract.is_wage_accurate)

    def test_monthly(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "amount": 5000.0,
                "amount_period": "month",
            }
        )

        self.assertEqual(contract.wage, 5000.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)

    def test_quarterly(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "amount": 15000.0,
                "amount_period": "quarter",
            }
        )

        self.assertEqual(contract.wage, 5000.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)

    def test_annual(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "name": "Contract",
                "employee_id": employee.id,
                "date_start": self.today,
                "date_end": self.today,
                "amount": 60000.0,
                "amount_period": "year",
            }
        )

        self.assertEqual(contract.wage, 5000.0)
        self.assertEqual(contract.approximate_wage, 0.0)
        self.assertTrue(contract.is_wage_accurate)
