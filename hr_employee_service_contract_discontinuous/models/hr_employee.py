# Copyright 2023 Punt Sistemes (https://puntsistemes.es)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.depends("service_start_date", "service_termination_date")
    def _compute_service_duration(self):
        for record in self:
            contracts = record.contract_ids.filtered(
                lambda x: x.state in self._get_service_contract_states()
            )
            service_duration = sum(contracts.mapped("contract_duration"))
            record.service_duration = service_duration

    @api.depends("service_start_date", "service_termination_date")
    def _compute_service_duration_display(self):
        for record in self:
            contracts_duration = record.service_duration
            service_duration = relativedelta(
                datetime(1970, 1, 1) + timedelta(days=contracts_duration),
                datetime(1970, 1, 1),
            )
            record.service_duration_years = service_duration.years
            record.service_duration_months = service_duration.months
            record.service_duration_days = service_duration.days

    def get_service_duration_from_date(self, date=None):
        self.ensure_one()
        today = fields.Date.today()
        if date and self.service_start_date and date > self.service_start_date:
            contracts = self.contract_ids.filtered(
                lambda x: x.state in self._get_service_contract_states()
            )
            current_contract = contracts.filtered(
                lambda x: (x.date_end or today) > date >= x.date_start
            )
            previous_contract = contracts.filtered(
                lambda x: date > (x.date_end or today)
            )

            current_duration = (
                (date - current_contract.date_start).days if current_contract else 0
            )
            previous_duration = sum(previous_contract.mapped("contract_duration"))
            total_duration = current_duration + previous_duration
        else:
            total_duration = 0

        service_duration = relativedelta(
            datetime(1970, 1, 1) + timedelta(days=total_duration), datetime(1970, 1, 1)
        )
        res = {
            "years": service_duration.years,
            "months": service_duration.months,
            "days": service_duration.days,
        }
        return res
