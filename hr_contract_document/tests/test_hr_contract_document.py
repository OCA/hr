# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from base64 import b64encode

from odoo import fields
from odoo.tests import common


class TestHrContractDocument(common.TransactionCase):
    def setUp(self):
        super().setUp()

        self.today = fields.Date.today()
        self.HrEmployee = self.env["hr.employee"]
        self.HrContract = self.env["hr.contract"]
        self.IrAttachment = self.env["ir.attachment"]

    def test(self):
        employee = self.HrEmployee.create({"name": "Employee"})
        contract = self.HrContract.create(
            {
                "employee_id": employee.id,
                "name": "Contract",
                "wage": 1000.0,
                "date_start": self.today,
                "date_end": self.today,
            }
        )
        attachment = self.IrAttachment.create(
            {
                "res_model": self.HrContract._name,
                "res_id": contract.id,
                "datas": b64encode(b"My attachment"),
                "name": "doc.txt",
            }
        )

        self.assertEqual(contract.documents_count, 1)
        self.assertIn(attachment, contract.document_ids)
        self.assertTrue(contract.action_get_attachment_tree_view())
