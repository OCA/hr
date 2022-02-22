# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    hours_report_last_update = fields.Date(
        help="Date from which start compute hours report"
    )

    @api.onchange("date_start")
    def onchange_date_start(self):
        if self.date_start:
            self.hours_report_last_update = self.date_start
