# Copyright 2025- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pytz
from dateutil.relativedelta import relativedelta

from odoo import fields, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    def _get_contract_work_entries_values(self, date_start, date_stop):
        contract_vals = super()._get_contract_work_entries_values(date_start, date_stop)

        start_dt = (
            pytz.utc.localize(date_start) if not date_start.tzinfo else date_start
        )
        end_dt = pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop
        result = dict()
        for calendar in self.mapped("resource_calendar_id"):
            result.update(calendar._get_unusual_days(start_dt, end_dt))
        weekends = []
        for we_date in result:
            if result[we_date]:
                weekends.append(we_date)

        timesheets = self.env["account.analytic.line"].search(
            [
                ("date", "in", weekends),
                ("project_id", "!=", False),
                ("holiday_id", "=", False),
                ("global_leave_id", "=", False),
            ]
        )

        for contract in self:
            new_work_entry_dates = []
            for timesheet in timesheets.filtered(
                lambda aal: aal.employee_id == contract.employee_id
            ):
                if (
                    not timesheet._get_work_entry()
                    and timesheet.date not in new_work_entry_dates
                ):
                    new_work_entry_dates.append(timesheet.date)
                    leave_entry_type = self.env.ref(
                        "hr_work_entry_timesheet_weekend.work_entry_type_leave"
                    )
                    date_start = (
                        pytz.timezone(contract.resource_calendar_id.tz)
                        .localize(fields.Datetime().to_datetime(timesheet.date))
                        .astimezone(pytz.UTC)
                        .replace(tzinfo=None)
                    )
                    contract_vals += [
                        dict(
                            [
                                (
                                    "name",
                                    "%s%s"
                                    % (
                                        leave_entry_type.name + ": "
                                        if leave_entry_type
                                        else "",
                                        contract.employee_id.name,
                                    ),
                                ),
                                ("date_start", date_start),
                                ("date_stop", date_start + relativedelta(minutes=1)),
                                ("work_entry_type_id", leave_entry_type.id),
                                ("employee_id", contract.employee_id.id),
                                ("company_id", contract.company_id.id),
                                ("state", "draft"),
                                ("contract_id", contract.id),
                            ]
                        )
                    ]
        return contract_vals
