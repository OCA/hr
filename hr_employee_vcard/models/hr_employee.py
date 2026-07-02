import base64

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    vcard_qr = fields.Binary(string="vCard ID")

    def action_generate_vcard(self):
        self.ensure_one()
        self.vcard_qr = self._get_vcard_qr()
        return self.action_print_vcard()

    def action_print_vcard(self):
        self.ensure_one()
        return self.env.ref("hr_employee_vcard.action_report_vcard").report_action(
            self, config=False
        )

    def _get_vcard_field_mapping(self):
        return {
            "logo": lambda employee: employee.company_id.logo,
            "name": lambda employee: employee.name,
            "job_title": lambda employee: employee.job_title,
            "work_email": lambda employee: employee.work_email,
            "work_phone": lambda employee: employee.work_phone,
            "company_name": lambda employee: employee.company_id.name,
            "website": lambda employee: employee.company_id.website,
            "qr": lambda employee: employee.vcard_qr,
        }

    def _get_vcard_content_mapping(self):
        return {
            "name": lambda value: f"FN:{value}",
            "job_title": lambda value: f"TITLE:{value}",
            "company_name": lambda value: f"ORG:{value}",
            "work_email": lambda value: f"EMAIL:{value}",
            "work_phone": lambda value: f"TEL;TYPE=WORK:{value}",
            "website": lambda value: f"URL:{value}",
        }

    def _get_vcard_content(self):
        self.ensure_one()
        field_mapping = self._get_vcard_field_mapping()
        content_mapping = self._get_vcard_content_mapping()
        lines = ["BEGIN:VCARD", "VERSION:3.0"]
        for field_name in self.company_id.vcard_layout_field_ids.mapped("field_name"):
            resolver = field_mapping.get(field_name)
            formatter = content_mapping.get(field_name)
            if resolver and formatter:
                value = resolver(self)
                if value:
                    lines.append(formatter(value))
        lines.append("END:VCARD")
        return "\n".join(lines)

    def _get_vcard_qr(self):
        self.ensure_one()
        if self.vcard_qr:
            return self.vcard_qr
        png = self.env["ir.actions.report"].barcode(
            "QR", self._get_vcard_content(), width=200, height=200
        )
        return base64.b64encode(png)

    def _get_vcard_values(self):
        self.ensure_one()
        employee = self.with_context(bin_size=False)
        selected_fields = employee.company_id.vcard_layout_field_ids.mapped(
            "field_name"
        )
        mapping = employee._get_vcard_field_mapping()
        values = {
            field_name: mapping[field_name](employee)
            for field_name in selected_fields
            if field_name in mapping
        }
        if "qr" in values:
            values["qr"] = employee._get_vcard_qr()
        return values

    def _get_vcard_card_data(self):
        self.ensure_one()
        return self.company_id._get_vcard_card_data(self._get_vcard_values())
