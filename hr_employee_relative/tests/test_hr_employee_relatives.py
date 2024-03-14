# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo.tests import Form, common


class TestHrEmployeeRelatives(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.Employee = self.env["hr.employee"]
        self.EmployeeRelative = self.env["hr.employee.relative"]
        self.relation_child = self.env.ref("hr_employee_relative.relation_child")
        self.relation_grandchild = self.env.ref(
            "hr_employee_relative.relation_grandchild"
        )
        self.relation_sibling = self.env.ref("hr_employee_relative.relation_sibling")

    def test_age_calculation(self):
        employee = self.Employee.create(
            {
                "name": "Employee",
                "relative_ids": [
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_sibling.id,
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
        self.assertEqual(relative.name, "Relative")
        # onchange partner
        with Form(relative) as f:
            f.partner_id = self.env.ref("base.res_partner_2")
            f.relation_id = self.relation_sibling
        self.assertEqual(relative.name, relative.partner_id.display_name)

    def test_children_calculation(self):
        employee = self.Employee.create(
            {
                "name": "Employee 2",
                "relative_ids": [
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_sibling.id,
                            "name": "Relative 1",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_child.id,
                            "name": "Relative 2",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_grandchild.id,
                            "name": "Relative 3",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_child.id,
                            "name": "Relative 4",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "relation_id": self.relation_child.id,
                            "name": "Relative 5",
                        },
                    ),
                ],
            }
        )

        grandchild = self.EmployeeRelative.browse(employee.relative_ids[2].id)
        child = self.EmployeeRelative.browse(employee.relative_ids[4].id)
        self.assertEqual(employee.children, 3)

        child.unlink()
        self.assertEqual(employee.children, 2)

        grandchild.relation_id = self.relation_child.id
        self.assertEqual(employee.children, 3)
