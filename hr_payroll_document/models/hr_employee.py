from odoo import _, models
from odoo.exceptions import ValidationError


class Employee(models.Model):
    _inherit = "hr.employee"

    def write(self, vals):
        res = super().write(vals)
        if "identification_id" in vals and not self.env["res.partner"].simple_vat_check(
            self.env.company.country_id.code, vals["identification_id"]
        ):
            raise ValidationError(_("The field identification ID is not valid"))
        return res
