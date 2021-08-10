# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests import common


class TestHrEmployeeDocument(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.Employee = self.env["hr.employee"]
        self.EmployeePublic = self.env["hr.employee.public"]
        self.SudoEmployee = self.Employee.sudo()
        self.Attachment = self.env["ir.attachment"]
        self.SudoAttachment = self.Attachment.sudo()
        self.employee_1 = self.SudoEmployee.create({"name": "Employee #1"})
        self.employee_2 = self.SudoEmployee.create({"name": "Employee #2"})

    def _create_attachment(self, employee_id):
        return self.SudoAttachment.create(
            {
                "res_model": self.Employee._name,
                "res_id": employee_id.id,
                "datas": base64.b64encode(b"My attachment"),
                "name": "doc.txt",
            }
        )

    def _create_user_from_employee(self, employee_id):
        user = self.env["res.users"].create(
            {
                "name": employee_id.name,
                "login": employee_id.name,
                "groups_id": [(6, 0, [self.env.ref("base.group_user").id])],
            }
        )
        employee_id.user_id = user.id
        return user

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
        # create records (users and attachments)
        user_manager = self.env["res.users"].create(
            {
                "name": "user_manager",
                "login": "user_manager",
                "groups_id": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("base.group_user").id,
                            self.env.ref("hr.group_hr_user").id,
                        ],
                    )
                ],
            }
        )
        user_1 = self._create_user_from_employee(self.employee_1)
        user_2 = self._create_user_from_employee(self.employee_2)
        attachment_1 = self._create_attachment(self.employee_1)
        attachment_2 = self._create_attachment(self.employee_2)
        # user_1
        records = self.Attachment.with_user(user_1).search([])
        self.assertTrue(attachment_1 in records)
        self.assertFalse(attachment_2 in records)
        # user_2
        records = self.Attachment.with_user(user_2).search([])
        self.assertFalse(attachment_1 in records)
        self.assertTrue(attachment_2 in records)
        # user_manager
        records = self.Attachment.with_user(user_manager).search([])
        self.assertTrue(attachment_1 in records)
        self.assertTrue(attachment_2 in records)
