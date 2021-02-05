# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import Form, common


class TestHrEmployeeRelatives(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.employee = self.env["hr.employee"].create(
            {
                "name": "Employee",
                "relative_ids": [
                    (
                        0,
                        0,
                        {
                            "relation_id": self.env.ref(
                                "hr_employee_relative.relation_sibling"
                            ).id,
                            "partner_id": self.env.ref("base.res_partner_1").id,
                            "name": "Relative",
                            "date_of_birth": datetime.now() + relativedelta(years=-42),
                        },
                    )
                ],
            }
        )

    def test_view_relatives(self):
        action = self.employee.action_view_relatives()
        self.assertEqual(action["domain"], [("employee_id", "=", self.employee.id)])

    def test_relatives_count(self):
        self.assertEqual(self.employee.relatives_count, 1)

    def test_age_calculation(self):
        relative = self.env["hr.employee.relative"].browse(
            self.employee.relative_ids[0].id
        )
        self.assertEqual(int(relative.age), 42)
        # onchange partner
        self.assertEqual(relative.name, "Relative")
        with Form(self.env["hr.employee.relative"]) as f:
            f.partner_id = self.env.ref("base.res_partner_2")
            f.relation_id = self.env.ref("hr_employee_relative.relation_sibling")
        relative = f.save()
        self.assertEqual(relative.name, relative.partner_id.display_name)
