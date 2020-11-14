# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import Form, common

_ns = "hr_employee_relative"


class TestHrEmployeeRelatives(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.Employee = self.env["hr.employee"]
        self.EmployeeRelative = self.env["hr.employee.relative"]

    def test_age_calculation(self):
        employee = self.Employee.create(
            {
                "name": "Employee",
                "relative_ids": [
                    (
                        0,
                        0,
                        {
                            "relation_id": self.env.ref(_ns + ".relation_sibling").id,
                            "partner_id": self.env.ref("base.res_partner_1").id,
                            "name": "Relative",
                            "date_of_birth": datetime.now() + relativedelta(years=-42),
                        },
                    )
                ],
            }
        )
        relative = self.EmployeeRelative.browse(employee.relative_ids[0].id)
        self.assertEqual(int(relative.age), 42)
        # onchange partner
        ctx = {
            "active_ids": [relative.id],
            "active_id": relative.id,
            "active_model": "hr.employee.relative",
        }
        self.assertEqual(relative.name, "Relative")
        with Form(self.EmployeeRelative.with_context(ctx)) as f:
            f.partner_id = self.env.ref("base.res_partner_2")
            f.relation_id = self.env.ref(_ns + ".relation_sibling")
        relative = f.save()
        self.assertEqual(relative.name, relative.partner_id.display_name)
