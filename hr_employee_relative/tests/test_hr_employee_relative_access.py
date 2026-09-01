# Copyright 2026 Grégory Mariani
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests import common
from odoo.tests.common import new_test_user


class TestHrEmployeeRelativeAccess(common.TransactionCase):
    """Regression test for the missing record rule on hr.employee.relative.

    The model granted base.group_user read access with no ir.rule, so any
    internal user could read every employee's family PII. A record rule now
    scopes normal users to their own employee's relatives while HR keeps full
    access.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Relative = cls.env["hr.employee.relative"]
        cls.relation = cls.env.ref("hr_employee_relative.relation_sibling")
        # A relative attached to an employee not linked to the plain user.
        cls.other_employee = cls.env["hr.employee"].create({"name": "Other Employee"})
        cls.foreign_relative = Relative.create(
            {
                "employee_id": cls.other_employee.id,
                "relation_id": cls.relation.id,
                "name": "Jane Secret",
                "date_of_birth": "1990-05-01",
                "phone_number": "+33600112233",
                "notes": "confidential",
            }
        )
        cls.plain_user = new_test_user(
            cls.env, login="relative-plain", groups="base.group_user"
        )
        cls.hr_user = new_test_user(
            cls.env,
            login="relative-hr",
            groups="base.group_user,hr.group_hr_user",
        )
        # An employee linked to the plain user, with its own relative.
        cls.own_employee = cls.env["hr.employee"].create(
            {"name": "Own Employee", "user_id": cls.plain_user.id}
        )
        cls.own_relative = Relative.create(
            {
                "employee_id": cls.own_employee.id,
                "relation_id": cls.relation.id,
                "name": "Own Relative",
            }
        )

    def test_plain_user_cannot_read_foreign_relatives(self):
        visible = self.env["hr.employee.relative"].with_user(self.plain_user).search([])
        self.assertNotIn(
            self.foreign_relative,
            visible,
            "a plain internal user must not read another employee's relatives",
        )

    def test_plain_user_reads_own_relatives(self):
        visible = self.env["hr.employee.relative"].with_user(self.plain_user).search([])
        self.assertIn(
            self.own_relative,
            visible,
            "a user must still see the relatives of their own employee record",
        )

    def test_hr_user_reads_all_relatives(self):
        visible = self.env["hr.employee.relative"].with_user(self.hr_user).search([])
        self.assertIn(
            self.foreign_relative,
            visible,
            "an HR user must retain full access to relatives",
        )
