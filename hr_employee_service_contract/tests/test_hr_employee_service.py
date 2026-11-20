# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common, tagged


@tagged("post_install", "-at_install")
class TestHrEmployeeService(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.today = fields.Date.today()
        cls.Employee = cls.env["hr.employee"]
        cls.SudoEmployee = cls.Employee.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create(
            {
                "name": "Employee #1",
                "date_version": self.today - relativedelta(years=3),
                "wage": 5000.0,
                "contract_date_start": self.today - relativedelta(years=3),
                "contract_date_end": self.today - relativedelta(years=1),
            }
        )

        self.assertEqual(
            employee.service_start_date, self.today - relativedelta(years=3)
        )
        self.assertEqual(
            employee.service_termination_date, self.today - relativedelta(years=1)
        )

    def test_2(self):
        employee = self.SudoEmployee.create(
            {
                "name": "Employee #2",
                "date_version": self.today - relativedelta(years=3),
                "wage": 5000.0,
                "contract_date_start": self.today - relativedelta(years=3),
            }
        )

        self.assertEqual(
            employee.service_start_date, self.today - relativedelta(years=3)
        )
        self.assertEqual(employee.service_termination_date, False)

    def test_3(self):
        employee = self.SudoEmployee.create(
            {
                "name": "Employee #3",
                "date_version": self.today - relativedelta(years=5),
                "wage": 5000.0,
                "contract_date_start": self.today - relativedelta(years=5),
                "contract_date_end": self.today - relativedelta(years=1),
            }
        )
        employee.create_version(
            {
                "date_version": self.today - relativedelta(months=6),
                "wage": 5000.0,
                "contract_date_start": self.today - relativedelta(months=6),
                "contract_date_end": False,
            }
        )

        self.assertEqual(
            employee.service_start_date, self.today - relativedelta(years=5)
        )
        self.assertEqual(employee.service_termination_date, False)

    def test_4(self):
        employee = self.SudoEmployee.create(
            {
                "name": "Employee #4",
                "date_version": self.today - relativedelta(years=5),
                "wage": 5000.0,
                "contract_date_start": self.today - relativedelta(years=5),
                "contract_date_end": self.today - relativedelta(years=1),
            }
        )
        employee.create_version(
            {
                "date_version": self.today - relativedelta(months=6),
                "wage": 5000.0,
                "contract_date_start": self.today - relativedelta(months=6),
                "contract_date_end": False,
            }
        )

        self.assertEqual(
            employee.service_start_date, self.today - relativedelta(years=5)
        )
        self.assertEqual(employee.service_termination_date, False)

    def test_5(self):
        employee = self.SudoEmployee.create({"name": "Employee #5"})

        self.assertEqual(employee.service_start_date, False)
        self.assertEqual(employee.service_termination_date, False)
