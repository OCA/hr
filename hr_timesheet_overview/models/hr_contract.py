# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "hr.contract"

    last_hours_report_date = fields.Date(
        help="Date from which start compute hours report"
    )

    @api.onchange("date_start")
    def onchange_date_start(self):
        if self.date_start:
            self.last_hours_report_date = self.date_start
