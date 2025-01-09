# Copyright 2025 INVITU SARL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    external_partner_id = fields.Many2one(
        "res.partner", related="employee_id.hr_external_partner_id", store=True
    )
    is_external = fields.Boolean(related="employee_id.is_external")
