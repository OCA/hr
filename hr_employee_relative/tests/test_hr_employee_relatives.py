# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import Form, common


class TestHrEmployeeRelatives(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.EmployeeRelative = cls.env["hr.employee.relative"]
        cls.relation_sibling = cls.env.ref("hr_employee_relative.relation_sibling")
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.partner_2 = cls.env.ref("base.res_partner_2")

    def create_relative(self, dob):
        employee = self.Employee.create(
            {
                "name": "Employee",
                "relative_ids": [
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_sibling.id,
                            "partner_id": self.partner_1.id,
                            "name": "Relative",
                            "date_of_birth": dob,
                        },
                    )
                ],
            }
        )
        return self.EmployeeRelative.browse(employee.relative_ids[0].id)

    def test_age_calculation_with_dob(self):
        dob = datetime.now() + relativedelta(years=-42, months=-3, days=-15)
        relative = self.create_relative(dob)

        expected_age = relativedelta(datetime.now(), dob)

        self.assertEqual(relative.age_year, expected_age.years)
        self.assertEqual(relative.age_month, expected_age.months)
        self.assertEqual(relative.age_day, expected_age.days)
        self.assertEqual(relative.name, "Relative")

        # Test onchange partner
        with Form(relative) as f:
            f.partner_id = self.partner_2
            f.relation_id = self.relation_sibling
        self.assertEqual(relative.name, relative.partner_id.display_name)

    def test_age_calculation_without_dob(self):
        relative = self.create_relative(False)

        self.assertEqual(relative.age_year, 0)
        self.assertEqual(relative.age_month, 0)
        self.assertEqual(relative.age_day, 0)
        self.assertEqual(relative.name, "Relative")
