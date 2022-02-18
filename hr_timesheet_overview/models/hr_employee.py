# Copyright 2022 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Contract(models.Model):
    _inherit = "hr.employee"

    last_hours_report_date = fields.Date(
        help="Date from which start compute hours report",
        compute="_compute_report_contract_date",
        store=True,
    )

    @api.depends("contract_ids.state", "contract_ids.last_hours_report_date")
    def _compute_report_contract_date(self):
        for employee in self:
            contracts = employee._get_first_contracts()
            if contracts:
                employee.last_hours_report_date = min(
                    contracts.mapped("last_hours_report_date")
                )
            else:
                employee.last_hours_report_date = False
