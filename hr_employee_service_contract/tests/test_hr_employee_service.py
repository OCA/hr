# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import common


class TestHrEmployeeService(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.now = fields.Datetime.now()
        self.Employee = self.env["hr.employee"]
        self.SudoEmployee = self.Employee.sudo()
        self.Contract = self.env["hr.contract"]
        self.SudoContract = self.Contract.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create(
            {
                "name": "Employee #1",
                "contract_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Employee #1 Contract #1",
                            "wage": 5000.0,
                            "state": "close",
                            "date_start": self.today - relativedelta(years=3),
                            "date_end": self.today - relativedelta(years=1),
                        },
                    )
                ],
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
                "contract_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Employee #2 Contract #1",
                            "wage": 5000.0,
                            "state": "open",
                            "date_start": self.today - relativedelta(years=3),
                        },
                    )
                ],
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
                "contract_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Employee #3 Contract #1",
                            "wage": 5000.0,
                            "state": "close",
                            "date_start": self.today - relativedelta(years=5),
                            "date_end": self.today - relativedelta(years=1),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Employee #3 Contract #2",
                            "wage": 5000.0,
                            "state": "open",
                            "date_start": self.today - relativedelta(months=6),
                        },
                    ),
                ],
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
                "contract_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Employee #4 Contract #1",
                            "wage": 5000.0,
                            "state": "close",
                            "date_start": self.today - relativedelta(years=5),
                            "date_end": self.today - relativedelta(years=1),
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": "Employee #4 Contract #2",
                            "wage": 5000.0,
                            "state": "close",
                            "date_start": self.today - relativedelta(months=6),
                        },
                    ),
                ],
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
