# Part of Odoo. See LICENSE file for full copyright and licensing details.
import base64

from odoo.modules.module import get_module_resource
from odoo.tests import common

from odoo.addons.mail.tests.common import mail_new_test_user


class TestHrPayrollDocument(common.TransactionCase):
    def setUp(self):
        super(TestHrPayrollDocument, self).setUp()
        self.env.user.tz = "Europe/Brussels"
        self.user_admin = self.env.ref("base.user_admin")

        # Fix Company without country
        self.env.company.country_id = False

        # Test users to use through the various tests
        self.user_employee = mail_new_test_user(
            self.env, login="david", groups="base.group_user"
        )
        self.user_employee_id = self.user_employee.id

        # Hr Data
        self.employee_emp = self.env["hr.employee"].create(
            {
                "name": "David Employee",
                "user_id": self.user_employee_id,
                "company_id": 1,
                "identification_id": "97641580W",
            }
        )
        self.employee_emp_id = self.employee_emp.id

        with open(
            get_module_resource("hr_payroll_document", "tests", "test.pdf"), "rb"
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
