# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests import new_test_user
from odoo.tests.common import users

from odoo.addons.base.tests.common import BaseCommon


class TestHrEmployeeDocument(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_1 = new_test_user(cls.env, login="test-user-1")
        cls.user_2 = new_test_user(cls.env, login="test-user-2")
        new_test_user(cls.env, login="test-user-manager", groups="hr.group_hr_user")
        cls.employee_1 = cls.env["hr.employee"].create(
            [{"name": "Employee #1", "user_id": cls.user_1.id}]
        )
        cls.employee_2 = cls.env["hr.employee"].create(
            [{"name": "Employee #2", "user_id": cls.user_2.id}]
        )

    @classmethod
    def _create_attachment(self, employee_id):
        return (
            self.env["ir.attachment"]
            .sudo()
            .create(
                [
                    {
                        "res_model": employee_id._name,
                        "res_id": employee_id.id,
                        "datas": base64.b64encode(b"My attachment"),
                        "name": "doc.txt",
                    }
                ]
            )
        )

    @classmethod
    def _get_attachments_from_employee(self, employee):
        res = employee.action_get_attachment_tree_view()
        return (
            self.env[res["res_model"]]
            .with_context(**res["context"])
            .search(res["domain"])
        )

    @users("test-user-1")
    def test_employee_attachment(self):
        employee = self.env.user.employee_id
        self._create_attachment(employee)
        self.assertEqual(employee.document_count, 1)
        employee_public = (
            self.env["hr.employee.public"]
            .browse(employee.id)
            .with_context(search_attachments_from_hr_employee=True)
        )
        self.assertEqual(employee_public.document_count, 1)

    @users("test-user-2")
    def test_employee_attachment_tree_view(self):
        employee = self.env.user.employee_id
        self.assertNotEqual(employee.action_get_attachment_tree_view(), None)
        employee_public = self.env["hr.employee.public"].browse(employee.id)
        items = self._get_attachments_from_employee(employee_public)
        self.assertEqual(len(items), 0)

    @users("test-user-1")
    def test_attachments_access_user_1(self):
        # create attachments
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        records = self._get_attachments_from_employee(self.env.user.employee_id)
        self.assertIn(attachment_1, records)
        self.assertNotIn(attachment_2, records)
        result_1 = self.env["ir.binary"]._find_record(
            None, "ir.attachment", attachment_1.id
        )
        self.assertTrue(result_1.env.su)

    @users("test-user-1")
    def test_attachments_access_user_1_web_search_read(self):
        self._create_attachment(self.employee_1)
        action = self.employee_1.action_get_attachment_tree_view()
        model = self.env["ir.attachment"].with_context(**action["context"])
        res = model.web_search_read(action["domain"], {"name": {}})
        self.assertEqual(res["length"], 1)

    @users("test-user-2")
    def test_attachments_access_user_2(self):
        # create attachments
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        records = self._get_attachments_from_employee(self.env.user.employee_id)
        self.assertNotIn(attachment_1, records)
        self.assertIn(attachment_2, records)
        result_2 = self.env["ir.binary"]._find_record(
            None, "ir.attachment", attachment_2.id
        )
        self.assertTrue(result_2.env.su)

    @users("test-user-manager")
    def test_attachments_access_user_manager(self):
        # create attachments
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        records = self.env["ir.attachment"].search([])
        self.assertIn(attachment_1, records)
        self.assertIn(attachment_2, records)

    @users("test-user-1")
    def test_check_access_read_employee(self):
        employee = self.env["hr.employee"].search(
            [("user_id", "=", self.env.user.id)], limit=1
        )
        self.assertTrue(employee, "Employee record for test-user-1 should exist")
        employee_with_context = employee.with_context(
            search_attachments_from_hr_employee=True
        )
        self.assertEqual(
            employee_with_context._name, "hr.employee", "Model should be hr.employee"
        )
        self.assertEqual(
            employee_with_context.check_access("read"),
            None,
            "Non-HR user should have read access with "
            "search_attachments_from_hr_employee context",
        )
        self.assertEqual(
            employee.check_access("read"),
            None,
            "Non-HR user should have read access to their own employee record",
        )
        other_employee = self.employee_2
        access = other_employee.check_access("read")
        self.assertFalse(
            access,
            "Non-HR user should not have read access to another employee's record",
        )

    @users("test-user-1")
    def test_compute_domain_coverage(self):
        domain = (
            self.env["ir.rule"]
            .with_context(search_attachments_from_hr_employee=True)
            ._compute_domain("hr.employee")
        )
        self.assertIsNotNone(domain)
