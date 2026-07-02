from odoo import fields, models


class HrEmployeeVcardField(models.Model):
    _name = "hr.employee.vcard.field"
    _description = "Employee vCard Field"
    _order = "sequence, id"

    sequence = fields.Integer(default=50)
    name = fields.Char(required=True, translate=True)
    field_name = fields.Selection(
        selection=[
            ("logo", "Logo"),
            ("name", "Name"),
            ("job_title", "Job Title"),
            ("work_email", "Work Email"),
            ("work_phone", "Work Phone"),
            ("company_name", "Company Name"),
            ("website", "Website"),
            ("qr", "QR"),
        ],
        required=True,
    )
