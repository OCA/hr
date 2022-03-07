# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "hr.employee"

    hours_report_last_update = fields.Date(
        help="Date from which start compute hours report",
        compute="_compute_report_contract_date",
        store=True,
    )

    @api.depends("contract_ids.state", "contract_ids.hours_report_last_update")
    def _compute_report_contract_date(self):
        for employee in self:
            employee.hours_report_last_update = (
                employee.contract_id.hours_report_last_update
            )

    def get_active_contracts(self):
        return self.contract_ids.filtered(lambda c: c.state == "open")
