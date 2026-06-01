# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
# Copyright 2023 Tecnativa - Pilar Vargas

from odoo.tests.common import TransactionCase


class TestHrAnnouncement(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.hr_department = cls.env["hr.department"].create({"name": "HR"})
        cls.sales_department = cls.env["hr.department"].create({"name": "Sales"})

        cls.manager_job = cls.env["hr.job"].create({"name": "Manager"})
        cls.developer_job = cls.env["hr.job"].create({"name": "Developer"})

        cls.user_a = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "User A",
                    "login": "user_a",
                    "email": "user_a@example.com",
                }
            )
        )

        cls.user_b = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "User B",
                    "login": "user_b",
                    "email": "user_b@example.com",
                }
            )
        )

        cls.user_c = (
            cls.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": "User C",
                    "login": "user_c",
                    "email": "user_c@example.com",
                }
            )
        )

        cls.employee_a = cls.env["hr.employee"].create(
            {
                "name": "Employee A",
                "user_id": cls.user_a.id,
                "department_id": cls.hr_department.id,
                "job_id": cls.manager_job.id,
            }
        )

        cls.employee_b = cls.env["hr.employee"].create(
            {
                "name": "Employee B",
                "user_id": cls.user_b.id,
                "department_id": cls.hr_department.id,
                "job_id": cls.developer_job.id,
            }
        )

        cls.employee_c = cls.env["hr.employee"].create(
            {
                "name": "Employee C",
                "user_id": cls.user_c.id,
                "department_id": cls.sales_department.id,
                "job_id": cls.developer_job.id,
            }
        )

    def _announcement_ids_for_user(self, user):
        result = user.with_user(user).announcement_user_count()
        return {rec["id"] for rec in result if isinstance(rec, dict)}

    def test_employee_announcement_visibility(self):
        announcement = self.env["announcement"].create(
            {
                "name": "Employee Announcement",
                "announcement_type": "employee",
                "employee_ids": [(6, 0, [self.employee_a.id])],
            }
        )

        announcement._compute_allowed_user_ids()

        self.assertIn(
            self.user_a,
            announcement.allowed_user_ids,
        )
        self.assertNotIn(
            self.user_b,
            announcement.allowed_user_ids,
        )
        self.assertNotIn(
            self.user_c,
            announcement.allowed_user_ids,
        )

    def test_department_announcement_visibility(self):
        announcement = self.env["announcement"].create(
            {
                "name": "Department Announcement",
                "announcement_type": "department",
                "department_ids": [(6, 0, [self.hr_department.id])],
            }
        )

        announcement._compute_allowed_user_ids()

        self.assertIn(
            self.user_a,
            announcement.allowed_user_ids,
        )
        self.assertIn(
            self.user_b,
            announcement.allowed_user_ids,
        )
        self.assertNotIn(
            self.user_c,
            announcement.allowed_user_ids,
        )

    def test_job_position_announcement_visibility(self):
        announcement = self.env["announcement"].create(
            {
                "name": "Developer Announcement",
                "announcement_type": "job_position",
                "position_ids": [(6, 0, [self.developer_job.id])],
            }
        )

        announcement._compute_allowed_user_ids()

        self.assertNotIn(
            self.user_a,
            announcement.allowed_user_ids,
        )
        self.assertIn(
            self.user_b,
            announcement.allowed_user_ids,
        )
        self.assertIn(
            self.user_c,
            announcement.allowed_user_ids,
        )

    def test_employee_announcement_write_employee_ids(self):
        announcement = self.env["announcement"].create(
            {
                "name": "Write Announcement",
                "announcement_type": "employee",
            }
        )

        announcement.write(
            {
                "employee_ids": [(6, 0, [self.employee_a.id])],
            }
        )

        self.assertEqual(
            announcement.employee_ids,
            self.employee_a,
        )

    def test_department_announcement_user_count(self):
        self.env["announcement"].create(
            {
                "name": "Department Count Announcement",
                "announcement_type": "department",
                "department_ids": [(6, 0, [self.hr_department.id])],
            }
        )

        result = self.user_a.with_user(self.user_a).announcement_user_count()

        self.assertIsInstance(result, list)

    def test_job_position_announcement_user_count(self):
        self.env["announcement"].create(
            {
                "name": "Job Count Announcement",
                "announcement_type": "job_position",
                "position_ids": [(6, 0, [self.developer_job.id])],
            }
        )

        result = self.user_b.with_user(self.user_b).announcement_user_count()

        self.assertIsInstance(result, list)

    def test_onchange_specific_users(self):
        announcement = self.env["announcement"].new(
            {
                "announcement_type": "specific_users",
            }
        )

        announcement.employee_ids = self.employee_a
        announcement.department_ids = self.hr_department
        announcement.position_ids = self.developer_job

        announcement._onchange_announcement_type()

        self.assertFalse(announcement.employee_ids)
        self.assertFalse(announcement.department_ids)
        self.assertFalse(announcement.position_ids)

    def test_onchange_user_group(self):
        announcement = self.env["announcement"].new(
            {
                "announcement_type": "user_group",
            }
        )

        announcement.employee_ids = self.employee_a
        announcement.department_ids = self.hr_department
        announcement.position_ids = self.developer_job

        announcement._onchange_announcement_type()

        self.assertFalse(announcement.employee_ids)
        self.assertFalse(announcement.department_ids)
        self.assertFalse(announcement.position_ids)

    def test_onchange_employee(self):
        announcement = self.env["announcement"].new(
            {
                "announcement_type": "employee",
            }
        )

        announcement.department_ids = self.hr_department
        announcement.position_ids = self.developer_job

        announcement._onchange_announcement_type()

        self.assertFalse(announcement.department_ids)
        self.assertFalse(announcement.position_ids)

    def test_onchange_department(self):
        announcement = self.env["announcement"].new(
            {
                "announcement_type": "department",
            }
        )

        announcement.employee_ids = self.employee_a
        announcement.position_ids = self.developer_job

        announcement._onchange_announcement_type()

        self.assertFalse(announcement.employee_ids)
        self.assertFalse(announcement.position_ids)

    def test_onchange_job_position(self):
        announcement = self.env["announcement"].new(
            {
                "announcement_type": "job_position",
            }
        )

        announcement.employee_ids = self.employee_a
        announcement.department_ids = self.hr_department

        announcement._onchange_announcement_type()

        self.assertFalse(announcement.employee_ids)
        self.assertFalse(announcement.department_ids)
