# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
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

    def test_employee_attachment(self):
        employee = self.SudoEmployee.create({"name": "Employee #1"})
        self.SudoAttachment.create(
            {
                "res_model": self.Employee._name,
                "res_id": employee.id,
                "datas": base64.b64encode(b"My attachment"),
                "name": "doc.txt",
            }
        )
        self.assertEqual(employee.document_count, 1)
        employee_public = self.EmployeePublic.browse(employee.id)
        self.assertEqual(employee_public.document_count, 1)

    def test_employee_attachment_tree_view(self):
        employee = self.SudoEmployee.create({"name": "Employee #2"})
        self.assertNotEqual(employee.action_get_attachment_tree_view(), None)
        employee_public = self.EmployeePublic.browse(employee.id)
        self.assertNotEqual(employee_public.action_get_attachment_tree_view(), None)
