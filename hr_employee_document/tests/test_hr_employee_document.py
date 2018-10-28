# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.tests import common


class TestHrEmployeeDocument(common.TransactionCase):

    def setUp(self):
        super().setUp()

        self.Employee = self.env['hr.employee']
        self.SudoEmployee = self.Employee.sudo()
        self.Attachment = self.env['ir.attachment']
        self.SudoAttachment = self.Attachment.sudo()

    def test_1(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #1',
        })
        attachment = self.SudoAttachment.create({
            'res_model': self.Employee._name,
            'res_id': employee.id,
            'datas': base64.b64encode(b'My attachment'),
            'name': 'doc.txt',
            'datas_fname': 'doc.txt',
        })

        self.assertEqual(employee.documents_count, 1)
        self.assertIn(attachment, employee.document_ids)

    def test_2(self):
        employee = self.SudoEmployee.create({
            'name': 'Employee #2',
        })
        self.assertNotEqual(employee.action_get_attachment_tree_view(), None)
