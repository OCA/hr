# Copyright 2024 Binhex (<https://binhex.cloud>)
# Copyright 2024 Binhex Ariel Barreiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    """Enhance the features of the employee adding phone's PIN and PUK codes."""

    _inherit = "hr.employee"

    mobile_phone_pin = fields.Char(
        "Mobile phone PIN",
        help="Corporate mobile's PIN, should be a 4 digit number",
        size=4,
    )
    mobile_phone_puk = fields.Char(
        "Mobile phone PUK",
        help="Corporate mobile's PUK, should be a 8 digit number",
        size=8,
    )

    @api.constrains("mobile_phone_pin", "mobile_phone_puk")
    def _check_mobile_phone_pin(self):
        for rec in self:
            if rec.mobile_phone_pin and (
                not rec.mobile_phone_pin.isdigit() or len(rec.mobile_phone_pin) != 4
            ):
                raise ValidationError(_("Mobile phone PIN should be a 4 digit number."))
            if rec.mobile_phone_puk and (
                not rec.mobile_phone_puk.isdigit() or len(rec.mobile_phone_puk) != 8
            ):
                raise ValidationError(_("Mobile phone PUK should be a 8 digit number."))


class EmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    mobile_phone_pin = fields.Char("Mobile phone PIN", readonly=True)
    mobile_phone_puk = fields.Char("Mobile phone PUK", readonly=True)

    is_current_user = fields.Boolean(compute="_compute_is_current_user")

    @api.depends("user_id")
    def _compute_is_current_user(self):
        for rec in self:
            rec.is_current_user = rec.user_id == self.env.user
