# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests import common, new_test_user
from odoo.tests.common import users


class TestHrEmployeeDocument(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.env = self.env(
            context=dict(
                self.env.context,
                mail_create_nolog=True,
                mail_create_nosubscribe=True,
                mail_notrack=True,
                no_reset_password=True,
                tracking_disable=True,
            )
        )
        self.user_1 = new_test_user(self.env, login="test-user-1")
        self.user_2 = new_test_user(self.env, login="test-user-2")
        new_test_user(self.env, login="test-user-manager", groups="hr.group_hr_user")
        self.employee_1 = self.env["hr.employee"].create(
            {"name": "Employee #1", "user_id": self.user_1.id}
        )
        self.employee_2 = self.env["hr.employee"].create(
            {"name": "Employee #2", "user_id": self.user_2.id}
        )

    def _create_attachment(self, employee_id):
        return (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "res_model": employee_id._name,
                    "res_id": employee_id.id,
                    "datas": base64.b64encode(b"My attachment"),
                    "name": "doc.txt",
                }
            )
        )

    @users("test-user-1")
    def test_employee_attachment(self):
        employee = self.env.user.employee_id
        self._create_attachment(employee)
        self.assertEqual(employee.document_count, 1)
        employee_public = self.env["hr.employee.public"].browse(employee.id)
        self.assertEqual(employee_public.document_count, 1)

    def _get_attachments_from_employee(self, employee):
        res = employee.action_get_attachment_tree_view()
        return (
            self.env[res["res_model"]]
            .with_context(**res["context"])
            .search(res["domain"])
        )

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

    @users("test-user-2")
    def test_attachments_access_user_2(self):
        # create attachments
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        records = self._get_attachments_from_employee(self.env.user.employee_id)
        self.assertNotIn(attachment_1, records)
        self.assertIn(attachment_2, records)

    @users("test-user-manager")
    def test_attachments_access_user_manager(self):
        # create attachments
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        records = self.env["ir.attachment"].search([])
        self.assertIn(attachment_1, records)
        self.assertIn(attachment_2, records)

    @users("test-user-1")
    def test_is_logged(self):
        employee = self.env.user.employee_id
        employee_public = self.env["hr.employee.public"].browse(employee.id)
        self.assertTrue(employee_public.is_logged)

        employee = self.employee_2
        employee_public = self.env["hr.employee.public"].browse(employee.id)
        self.assertFalse(employee_public.is_logged)
