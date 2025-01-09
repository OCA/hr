# Copyright 2025 INVITU SARL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class TimesheetsAnalysisReport(models.Model):
    _inherit = "timesheets.analysis.report"

    external_partner_id = fields.Many2one(
        "res.partner", string="External Partner", readonly=True
    )
    is_external = fields.Boolean(related="employee_id.is_external", readonly=True)

    @api.model
    def _select(self):
        return (
            super()._select()
            + """,
            A.external_partner_id AS external_partner_id
        """
        )
