import base64

from odoo import fields, models

PREVIEW_SAMPLE = {
    "name": "Marc Demo",
    "job_title": "Sales Manager",
    "work_email": "marc.demo@example.com",
    "work_phone": "+1 555 123 4567",
    "website": "https://www.example.com",
}


class ResCompany(models.Model):
    _name = "res.company"
    _inherit = ["res.company", "hr.employee.vcard.mixin"]

    vcard_layout_id = fields.Many2one(
        comodel_name="hr.employee.vcard.layout",
        default=lambda self: self.env.ref(
            "hr_employee_vcard.hr_employee_vcard_layout_modern",
            raise_if_not_found=False,
        ),
        string="Layout",
    )

    vcard_layout_background = fields.Selection(
        selection=[
            ("blank", "Blank"),
            ("demo-logo", "Demo Logo"),
            ("custom", "Custom"),
        ],
        default="blank",
        required=True,
        string="Background",
    )

    vcard_layout_background_image = fields.Binary(string="vCard Background Image")

    vcard_layout_font = fields.Selection(
        selection=[
            ("lato", "Lato"),
            ("roboto", "Roboto"),
            ("open-sans", "Open Sans"),
            ("montserrat", "Montserrat"),
            ("oswald", "Oswald"),
            ("raleway", "Raleway"),
            ("tajawal", "Tajawal"),
            ("fira-mono", "Fira Mono"),
        ],
        default="lato",
        required=True,
        string="Text",
    )

    vcard_layout_field_ids = fields.Many2many(
        comodel_name="hr.employee.vcard.field",
        default=lambda self: self._default_vcard_layout_field_ids(),
        string="Fields",
    )

    def _default_vcard_layout_field_ids(self):
        xmlids = [
            "hr_employee_vcard.hr_employee_vcard_field_logo",
            "hr_employee_vcard.hr_employee_vcard_field_company_name",
            "hr_employee_vcard.hr_employee_vcard_field_qr",
            "hr_employee_vcard.hr_employee_vcard_field_name",
            "hr_employee_vcard.hr_employee_vcard_field_job_title",
            "hr_employee_vcard.hr_employee_vcard_field_work_email",
            "hr_employee_vcard.hr_employee_vcard_field_work_phone",
            "hr_employee_vcard.hr_employee_vcard_field_website",
        ]
        return self.env["hr.employee.vcard.field"].browse(
            [
                record.id
                for record in (
                    self.env.ref(xmlid, raise_if_not_found=False) for xmlid in xmlids
                )
                if record
            ]
        )

    def _get_vcard_preview_values(self):
        """Sample values for the preview (current user's employee + fallbacks)."""
        self.ensure_one()
        company = self.with_context(bin_size=False)
        employee = self.env.user.employee_id
        return {
            "logo": company.logo,
            "name": employee.name or PREVIEW_SAMPLE["name"],
            "job_title": employee.job_title or PREVIEW_SAMPLE["job_title"],
            "work_email": employee.work_email or PREVIEW_SAMPLE["work_email"],
            "work_phone": employee.work_phone or PREVIEW_SAMPLE["work_phone"],
            "company_name": company.name,
            "website": company.website or PREVIEW_SAMPLE["website"],
            "qr": (employee.vcard_qr if employee else False)
            or self._get_vcard_preview_qr(),
        }

    def _get_vcard_preview_qr(self):
        png = self.env["ir.actions.report"].barcode(
            "QR",
            f"BEGIN:VCARD\nVERSION:3.0\nFN:{PREVIEW_SAMPLE['name']}\nEND:VCARD",
            width=200,
            height=200,
        )
        return base64.b64encode(png)
