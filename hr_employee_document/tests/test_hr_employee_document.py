# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests import common, new_test_user


class TestHrEmployeeDocument(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.Employee = self.env["hr.employee"]
        self.EmployeePublic = self.env["hr.employee.public"]
        self.SudoEmployee = self.Employee.sudo()
        self.Attachment = self.env["ir.attachment"]
        self.SudoAttachment = self.Attachment.sudo()
        self.user_1 = new_test_user(
            self.env,
            login="Test user employee 1",
        )
        self.user_2 = new_test_user(
            self.env,
            login="Test user employee 2",
        )
        self.user_manager = new_test_user(
            self.env,
            login="Test user manager",
            groups="hr.group_hr_user",
        )
        self.employee_1 = (
            self.SudoEmployee.create({"name": "Employee #1", "user_id": self.user_1.id})
        ).with_user(self.user_1)
        self.employee_2 = (
            self.SudoEmployee.create({"name": "Employee #2", "user_id": self.user_2.id})
        ).with_user(self.user_2)

    def _create_attachment(self, employee_id):
        return self.SudoAttachment.create(
            {
                "res_model": self.Employee._name,
                "res_id": employee_id.id,
                "datas": base64.b64encode(b"My attachment"),
                "name": "doc.txt",
            }
        )

    def test_employee_attachment(self):
        self._create_attachment(self.employee_1)
        self.assertEqual(self.employee_1.document_count, 1)
        employee_public = self.EmployeePublic.browse(self.employee_1.id)
        self.assertEqual(employee_public.document_count, 1)

    def test_employee_attachment_tree_view(self):
        self.assertNotEqual(self.employee_2.action_get_attachment_tree_view(), None)
        employee_public = self.EmployeePublic.browse(self.employee_2.id)
        self.assertNotEqual(employee_public.action_get_attachment_tree_view(), None)

    def test_attachments_access(self):
        # create attachments
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        # user_1
        records = self.Attachment.with_user(self.user_1).search([])
        self.assertTrue(attachment_1 in records)
        self.assertFalse(attachment_2 in records)
        # user_2
        records = self.Attachment.with_user(self.user_2).search([])
        self.assertFalse(attachment_1 in records)
        self.assertTrue(attachment_2 in records)
        # user_manager
        records = self.Attachment.with_user(self.user_manager).search([])
        self.assertTrue(attachment_1 in records)
        self.assertTrue(attachment_2 in records)
