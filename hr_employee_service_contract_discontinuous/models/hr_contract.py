# Copyright 2023 Punt Sistemes (https://puntsistemes.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from math import fabs

from odoo import api, fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    contract_duration = fields.Integer(
        groups="hr.group_hr_user",
        readonly=True,
        compute="_compute_contract_duration",
        help="Contract duration in days",
    )

    @api.depends("date_start", "date_end", "state")
    def _compute_contract_duration(self):
        contract_states = self.env["hr.employee"]._get_service_contract_states()
        for record in self:
            contract_end = record.date_end or fields.Date.today()
            if (
                record.state in contract_states
                and record.date_start
                and contract_end > record.date_start
            ):
                contract_duration = int(
                    fabs((contract_end - record.date_start) / timedelta(days=1))
                )
            else:
                contract_duration = 0
            record.contract_duration = contract_duration
