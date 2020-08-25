# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    identification_type_id = fields.Many2one(
        related="employee_id.identification_type_id", readonly=False, related_sudo=False
    )
    identification_expiry_date = fields.Date(
        related="employee_id.identification_expiry_date",
        readonly=False,
        related_sudo=False,
    )
