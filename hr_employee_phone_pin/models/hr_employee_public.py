# Copyright 2024 Binhex (<https://binhex.cloud>)
# Copyright 2024 Binhex Ariel Barreiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class EmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    mobile_phone_pin = fields.Char(
        related="employee_id.mobile_phone_pin", readonly=True
    )
    mobile_phone_puk = fields.Char(
        related="employee_id.mobile_phone_puk", readonly=True
    )

    is_current_user = fields.Boolean(compute="_compute_is_current_user")

    @api.depends("user_id")
    def _compute_is_current_user(self):
        for rec in self:
            rec.is_current_user = rec.user_id == self.env.user
