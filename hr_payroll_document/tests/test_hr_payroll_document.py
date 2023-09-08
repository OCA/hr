import base64

from odoo import _
from odoo.exceptions import UserError, ValidationError
from odoo.modules.module import get_module_resource

from odoo.addons.hr_payroll_document.tests.common import TestHrPayrollDocument


class TestHRPayrollDocument(TestHrPayrollDocument):
    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)

    def fill_company_id(self):
        self.env.company.country_id = self.env["res.country"].search(
            [("name", "=", "Spain")]
        )

    def test_extension_error(self):
        with open(
            get_module_resource("hr_payroll_document", "tests", "test.docx"), "rb"
        ) as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())
        ir_values = {
            "name": "test",
            "type": "binary",
            "datas": encoded_string,
            "store_fname": encoded_string,
            "res_model": "payroll.management.wizard",
            "res_id": 1,
        }
        self.attachment = self.env["ir.attachment"].create(ir_values)
        self.month = "January"
        self.wizard = self.env["payroll.management.wizard"].create(
            {"payrolls": [self.attachment.id], "month": self.month}
        )
        with self.assertRaises(ValidationError):
            self.wizard.send_payrolls()

    def test_company_id_required(self):
        with self.assertRaises(UserError):
            self.wizard.send_payrolls()

    def test_employee_vat_not_valid(self):
        self.fill_company_id()
        with self.assertRaises(ValidationError):
            employees = self.env["hr.employee"].search([])
            for employee in employees:
                if not employee.identification_id:
                    employee.identification_id = "XXXXXXX"

    def test_one_employee_not_found(self):
        self.fill_company_id()
        employees = self.env["hr.employee"].search([])
        for employee in employees:
            if not employee.identification_id:
                employee.identification_id = "19827654K"
        self.assertEqual(
            self.wizard.send_payrolls(),
            {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Employees not found"),
                    "message": _("IDs whose employee has not been found: ")
                    + "88207408Q",
                    "sticky": True,
                    "type": "warning",
                    "next": {
                        "name": _("Payrolls sent"),
                        "type": "ir.actions.act_window",
                        "res_model": "hr.employee",
                        "views": [
                            (
                                self.env.ref("hr.hr_employee_public_view_kanban").id,
                                "list",
                            )
                        ],
                    },
                },
            },
        )

    def test_send_payrolls_correctly(self):
        self.fill_company_id()
        employees = self.env["hr.employee"].search([])
        for employee in employees:
            if not employee.identification_id:
                if employee.id == 1:
                    employee.identification_id = "88207408Q"
                else:
                    employee.identification_id = "33146124L"
        self.assertEqual(
            self.wizard.send_payrolls(),
            {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Payrolls sent"),
                    "message": _("Payrolls sent to employees correctly"),
                    "sticky": False,
                    "type": "success",
                    "next": {
                        "name": _("Payrolls sent"),
                        "type": "ir.actions.act_window",
                        "res_model": "hr.employee",
                        "views": [
                            (
                                self.env.ref("hr.hr_employee_public_view_kanban").id,
                                "list",
                            )
                        ],
                    },
                },
            },
        )
