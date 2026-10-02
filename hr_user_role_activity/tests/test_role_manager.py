from freezegun import freeze_time

from odoo import fields
from odoo.tests.common import TransactionCase, tagged

ACTIVITY_XMLID = "base_user_role_activity.mail_activity_role_expire"


@tagged("post_install", "-at_install")
class TestRoleManager(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env["res.company"].create({"name": "Company A"})
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})

        cls.manager_user_a = cls.env["res.users"].create(
            {
                "name": "Manager A",
                "login": "manager_a_role_activity",
                "company_id": cls.company_a.id,
                "company_ids": [fields.Command.set([cls.company_a.id])],
            }
        )
        cls.manager_user_b = cls.env["res.users"].create(
            {
                "name": "Manager B",
                "login": "manager_b_role_activity",
                "company_id": cls.company_b.id,
                "company_ids": [fields.Command.set([cls.company_b.id])],
            }
        )
        cls.user = cls.env["res.users"].create(
            {
                "name": "Employee User",
                "login": "employee_user_role_activity",
                "company_id": cls.company_a.id,
                "company_ids": [
                    fields.Command.set([cls.company_a.id, cls.company_b.id])
                ],
            }
        )
        cls.manager_employee_a = cls.env["hr.employee"].create(
            {
                "name": "Manager Employee A",
                "user_id": cls.manager_user_a.id,
                "company_id": cls.company_a.id,
            }
        )
        cls.manager_employee_b = cls.env["hr.employee"].create(
            {
                "name": "Manager Employee B",
                "user_id": cls.manager_user_b.id,
                "company_id": cls.company_b.id,
            }
        )
        cls.env["hr.employee"].create(
            {
                "name": "Employee in A",
                "user_id": cls.user.id,
                "company_id": cls.company_a.id,
                "parent_id": cls.manager_employee_a.id,
            }
        )
        cls.env["hr.employee"].create(
            {
                "name": "Employee in B",
                "user_id": cls.user.id,
                "company_id": cls.company_b.id,
                "parent_id": cls.manager_employee_b.id,
            }
        )

        cls.role = cls.env["res.users.role"].create({"name": "Test Role"})
        cls.env["res.users.role.line"].create(
            {
                "user_id": cls.user.id,
                "role_id": cls.role.id,
                "date_from": fields.Date.from_string("2024-01-01"),
                "date_to": fields.Date.from_string("2025-02-01"),
            }
        )

    def _get_activities(self):
        return self.user.partner_id.activity_search([ACTIVITY_XMLID])

    def _user_in_company(self, company):
        return (
            self.env["res.users"]
            .with_context(allowed_company_ids=[company.id])
            .browse(self.user.id)
        )

    @freeze_time("2025-01-15")
    def test_manager_from_current_company_is_assigned(self):
        self._get_activities().unlink()
        self._user_in_company(self.company_a).activity_update_role_reminder()
        self.assertEqual(self._get_activities().user_id, self.manager_user_a)

    @freeze_time("2025-01-15")
    def test_manager_from_company_b_is_assigned(self):
        self._get_activities().unlink()
        self._user_in_company(self.company_b).activity_update_role_reminder()
        self.assertEqual(self._get_activities().user_id, self.manager_user_b)

    @freeze_time("2025-01-15")
    def test_fallback_to_other_company_manager(self):
        """When env.company has no matching employee, fall back to the first one."""
        self._get_activities().unlink()
        company_c = self.env["res.company"].create({"name": "Company C"})
        self._user_in_company(company_c).activity_update_role_reminder()
        self.assertIn(
            self._get_activities().user_id,
            self.manager_user_a | self.manager_user_b,
        )

    @freeze_time("2025-01-15")
    def test_no_manager_falls_back_to_user(self):
        """Without an employee record the activity stays with the user."""
        standalone_user = self.env["res.users"].create(
            {"name": "Standalone User", "login": "standalone_role_activity"}
        )
        self.env["res.users.role.line"].create(
            {
                "user_id": standalone_user.id,
                "role_id": self.role.id,
                "date_from": fields.Date.from_string("2024-01-01"),
                "date_to": fields.Date.from_string("2025-02-01"),
            }
        )
        standalone_user.activity_update_role_reminder()
        activities = standalone_user.partner_id.activity_search([ACTIVITY_XMLID])
        self.assertEqual(activities.user_id, standalone_user)
