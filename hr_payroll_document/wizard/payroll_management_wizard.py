import base64
from base64 import b64decode

from pypdf import PdfReader, PdfWriter

from odoo import _, fields, models
from odoo.exceptions import UserError, ValidationError


class PayrollManagamentWizard(models.TransientModel):
    _name = "payroll.management.wizard"
    _description = "Payroll Management"

    month = fields.Char()
    payrolls = fields.Many2many(
        "ir.attachment",
        "payrol_rel",
        "doc_id",
        "attach_id3",
        copy=False,
    )

    def send_payrolls(self):
        not_found = set()
        self.merge_pdfs()
        reader = PdfReader("/tmp/merged-pdf.pdf")
        employees = set()

        # Validate if company have country
        if not self.env.company.country_id:
            raise UserError(_("You must to filled country field of company"))

        # Find all IDs of the employees
        for page in reader.pages:
            for value in page.extract_text().split():
                if self.validate_id(value) and value != self.env.company.vat:
                    employee = self.env["hr.employee"].search(
                        [("identification_id", "=", value)]
                    )
                    if employee:
                        employees.add(employee)
                    else:
                        not_found.add(value)
                    break

        for employee in list(employees):
            pdfWriter = PdfWriter()
            for page in reader.pages:
                if employee.identification_id in page.extract_text():
                    # Save pdf with payrolls of employee
                    pdfWriter.add_page(page)

            path = "/tmp/" + _("Payroll ") + employee.name + ".pdf"

            # Encrypt the payroll file with the identification identifier of the employee
            pdfWriter.encrypt(employee.identification_id, algorithm="AES-256")

            f = open(path, "wb")
            pdfWriter.write(f)
            f.close()

            # Send payroll to the employee
            self.send_mail(employee, path)

        if not_found:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Employees not found"),
                    "message": _("IDs whose employee has not been found: ")
                    + ", ".join(list(not_found)),
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
            }

        return {
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
                        (self.env.ref("hr.hr_employee_public_view_kanban").id, "list")
                    ],
                },
            },
        }

    def merge_pdfs(self):
        # Merge the pdfs together
        pdfs = []
        for file in self.payrolls:
            b64 = file.datas
            btes = b64decode(b64, validate=True)
            if btes[0:4] != b"%PDF":
                raise ValidationError(_("Missing pdf file signature"))
            f = open("/tmp/" + file.name, "wb")
            f.write(btes)
            f.close()
            pdfs.append(f.name)

        merger = PdfWriter()

        for pdf in pdfs:
            merger.append(pdf)

        merger.write("/tmp/merged-pdf.pdf")
        merger.close()

    def send_mail(self, employee, path):
        # Open Payrolls of employee and encode content
        with open(path, "rb") as pdf_file:
            encoded_string = base64.b64encode(pdf_file.read())

        # Attach file to email
        ir_values = {
            "name": _("Payroll") + "_" + self.month + "_" + employee.name,
            "type": "binary",
            "datas": encoded_string,
            "store_fname": encoded_string,
            "res_model": "hr.employee",
            "res_id": employee.id,
        }

        # Save payroll attachment to all employee payrolls attachments
        self.env["ir.attachment.payroll.custom"].create(
            {
                "attachment_id": self.env["ir.attachment"].create(ir_values).id,
                "employee": employee.name,
                "month": self.month,
                "identification_id": employee.identification_id,
            }
        )

        # Send mail
        mail_template = self.env.ref(
            "hr_payroll_document.payroll_employee_email_template"
        )
        data_id = [(6, 0, [self.env["ir.attachment"].create(ir_values).id])]
        mail_template.attachment_ids = data_id
        mail_template.with_context(**{"month": self.month}).send_mail(
            employee.user_id.id, force_send=True
        )

    def validate_id(self, number):
        return self.env["res.partner"].simple_vat_check(
            self.env.company.country_id.code, number
        )
