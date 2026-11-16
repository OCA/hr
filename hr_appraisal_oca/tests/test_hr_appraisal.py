# Copyright 2025 Fundación Esment - Estefanía Bauzá Illán
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import Command
from odoo.tests import new_test_user

from odoo.addons.base.tests.common import BaseCommon


class TestHrAppraisalEmployee(BaseCommon):
    _test_user_groups = ("base.group_user", "hr.group_hr_user")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Employee = cls.env["hr.employee"]
        cls.User = cls.env["res.users"]
        cls.Template = cls.env["hr.appraisal.template"]
        cls.Tag = cls.env["hr.appraisal.tag"]
        cls.Appraisal = cls.env["hr.appraisal"]
        cls.user_manager = new_test_user(
            cls.env,
            login="manager@example.com",
            email="manager@example.com",
            groups="hr.group_hr_user,hr_appraisal_oca.group_appraisal_user",
        )
        cls.employee_user = cls.User.create(
            {
                "name": "Employee User",
                "login": "employee@example.com",
                "email": "employee@example.com",
            }
        )
        cls.department_1 = cls.env["hr.department"].create({"name": "Department 1"})
        cls.manager = cls.Employee.create(
            {
                "name": "Manager",
                "user_id": cls.user_manager.id,
                "work_email": "manager@example.com",
                "department_id": cls.department_1.id,
            }
        )
        cls.employee = cls.Employee.create(
            {
                "name": "Employee",
                "user_id": cls.employee_user.id,
                "parent_id": cls.manager.id,
                "work_email": "employee@example.com",
                "department_id": cls.department_1.id,
            }
        )
        cls.template = cls.Template.create(
            {
                "description": "Default Template",
                "appraisal_employee_feedback_template": "<p>Feedback</p>",
                "appraisal_manager_feedback_template": "<p>Manager Feedback</p>",
            }
        )
        cls.env["ir.config_parameter"].sudo().set_int(
            "hr_appraisal_oca.default_appraisal_template_id", cls.template.id
        )
        cls.tag = cls.Tag.create(
            {
                "name": "Performance",
                "color": 1,
            }
        )
        cls.appraisal = cls.Appraisal.create(
            {
                "employee_id": cls.employee.id,
                "manager_ids": [Command.link(cls.manager.id)],
                "date_close": "2025-12-31",
                "state": "1_new",
                "tag_ids": [(6, 0, [cls.tag.id])],
            }
        )

    def test_appraisal_creation(self):
        self.assertEqual(self.appraisal.state, "1_new")
        self.assertEqual(self.appraisal.employee_id, self.employee)
        self.assertIn(self.manager, self.appraisal.manager_ids)
        self.assertEqual(self.appraisal.appraisal_template_id, self.template)
        self.assertIn(self.tag, self.appraisal.tag_ids)

    def test_action_confirm_visibility_all(self):
        appraisal = self.appraisal.with_user(self.user_manager)
        appraisal.visibility = "all"
        appraisal.action_confirm()
        self.assertEqual(appraisal.state, "2_pending")
        self.assertFalse(appraisal.employee_feedback_published)
        self.assertFalse(appraisal.manager_feedback_published)
        self.assertEqual(len(appraisal.activity_ids), 2)

    def test_action_confirm_visibility_manager(self):
        appraisal = self.appraisal.with_user(self.user_manager)
        appraisal.visibility = "manager"
        appraisal.action_confirm()
        self.assertEqual(appraisal.state, "2_pending")
        self.assertEqual(len(appraisal.activity_ids), 1)
        activity = appraisal.activity_ids[0]
        self.assertEqual(activity.user_id, self.user_manager)

    def test_action_done(self):
        appraisal = self.appraisal.with_user(self.user_manager)
        appraisal.action_confirm()
        appraisal.action_done()
        self.assertEqual(appraisal.state, "3_done")
        self.assertTrue(appraisal.employee_feedback_published)
        self.assertTrue(appraisal.manager_feedback_published)

    def test_action_done_visibility_manager(self):
        appraisal = self.appraisal.with_user(self.user_manager)
        appraisal.visibility = "manager"
        appraisal.action_confirm()
        appraisal.action_done()
        self.assertEqual(appraisal.state, "3_done")
        self.assertTrue(appraisal.employee_feedback_published)
        self.assertTrue(appraisal.manager_feedback_published)

    def test_publish_employee_feedback_toggle(self):
        appraisal = self.appraisal.with_user(self.user_manager)
        published = appraisal.employee_feedback_published
        appraisal.action_publish_employee_feedback()
        self.assertNotEqual(appraisal.employee_feedback_published, published)

    def test_publish_manager_feedback_toggle(self):
        appraisal = self.appraisal.with_user(self.user_manager)
        published = appraisal.manager_feedback_published
        appraisal.action_publish_manager_feedback()
        self.assertNotEqual(appraisal.manager_feedback_published, published)

    def test_default_template_assigned(self):
        self.assertEqual(self.appraisal.appraisal_template_id, self.template)
        self.assertEqual(
            self.appraisal.employee_feedback,
            Markup(self.template.appraisal_employee_feedback_template),
        )
        self.assertEqual(
            self.appraisal.manager_feedback,
            Markup(self.template.appraisal_manager_feedback_template),
        )

    def test_manager_permissions_follow_hierarchy(self):
        replacement = new_test_user(self.env, login="replacement@example.com")
        self.assertIn(self.user_manager, self.employee.allowed_user_ids)
        self.manager.user_id = replacement
        self.assertNotIn(self.user_manager, self.employee.allowed_user_ids)
        self.assertIn(replacement, self.employee.allowed_user_ids)
        director = self.Employee.create(
            {"name": "Director", "user_id": self.user_manager.id}
        )
        self.manager.parent_id = director
        self.assertIn(self.user_manager, self.employee.allowed_user_ids)
        self.manager.parent_id = False
        self.assertNotIn(self.user_manager, self.employee.allowed_user_ids)

    def test_search_last_appraisal(self):
        latest = self.appraisal.copy()
        self.assertEqual(self.employee.last_appraisal_id, latest)
        self.assertNotIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "=", self.appraisal.id)]),
        )
        self.assertIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "=", latest.id)]),
        )
        self.assertNotIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "=", False)]),
        )
        self.assertIn(
            self.manager,
            self.Employee.search([("last_appraisal_id", "=", False)]),
        )
        self.assertIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "!=", False)]),
        )
        self.assertNotIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "!=", latest.id)]),
        )

    def test_open_ongoing_before_latest_completed(self):
        latest = self.appraisal.copy({"state": "3_done"})
        self.assertEqual(self.employee.last_appraisal_id, latest)
        action = self.employee.action_open_last_appraisal()
        self.assertEqual(action["res_id"], self.appraisal.id)
        second = self.appraisal.copy()
        action = self.employee.action_open_last_appraisal()
        self.assertEqual(action["view_mode"], "list,form")
        self.assertEqual(
            set(self.Appraisal.search(action["domain"]).ids),
            {self.appraisal.id, second.id},
        )

    def test_assigned_manager_can_open_appraisal(self):
        assigned_user = new_test_user(
            self.env,
            login="assigned@example.com",
            groups="hr_appraisal_oca.group_appraisal_user,hr.group_hr_user",
        )
        assigned_manager = self.Employee.create(
            {"name": "Assigned manager", "user_id": assigned_user.id}
        )
        self.appraisal.manager_ids = assigned_manager
        employee = self.employee.with_user(assigned_user)
        self.assertTrue(employee.can_open_last_appraisal)
        self.assertEqual(
            employee.action_open_last_appraisal()["res_id"], self.appraisal.id
        )

    def test_last_appraisal_uses_creation_date_before_id(self):
        newer_id = self.appraisal.copy()
        # Odoo does not allow changing audit dates through write().
        newer_id.flush_recordset()
        self.env.cr.execute(
            "UPDATE hr_appraisal SET create_date = %s WHERE id = %s",
            ["2000-01-01 00:00:00", newer_id.id],
        )
        newer_id.invalidate_recordset(["create_date"])
        newer_id.modified(["create_date"])
        self.assertEqual(self.employee.last_appraisal_id, self.appraisal)
        self.assertIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "=", self.appraisal.id)]),
        )
        self.assertNotIn(
            self.employee,
            self.Employee.search([("last_appraisal_id", "=", newer_id.id)]),
        )

    def test_last_appraisal_respects_access_rules(self):
        self.employee_user.sudo().group_ids |= self.env.ref(
            "hr_appraisal_oca.group_appraisal_user"
        ) | self.env.ref("hr.group_hr_user")
        hidden = self.appraisal.copy({"visibility": "manager"})
        employee = self.employee.with_user(self.employee_user)
        self.assertEqual(employee.last_appraisal_id, self.appraisal)
        self.assertIn(
            employee,
            employee.search([("last_appraisal_id", "=", self.appraisal.id)]),
        )
        self.assertNotIn(
            employee,
            employee.search([("last_appraisal_id", "=", hidden.id)]),
        )
