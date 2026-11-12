# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from collections import defaultdict

import pytz

from odoo import api, fields, models

from odoo.addons.hr_work_entry_contract.models.hr_work_intervals import WorkIntervals


class HrContract(models.Model):
    _inherit = "hr.contract"

    work_entry_source = fields.Selection(
        selection_add=[("attendance_oca", "Attendances")],
        ondelete={"attendance_oca": "set default"},
    )

    def _get_hr_attendances(self, start_dt, end_dt):
        return self.env["hr.attendance"].search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("check_in", "<", end_dt),
                ("check_out", ">", start_dt),
            ]
        )

    @api.model
    def _hr_attendances_to_work_intervals(
        self, hr_attendances, default_check_out_dt=None
    ):
        intervals = []
        # the dates in the intervals in contract_intervals have a
        # timezone, while the check_in and check_out fields of hr.attendance
        # are naive utc datetime values. the returned intervals must contain
        # dates with a timezone.
        for hr_attendance in hr_attendances:
            intervals.append(
                (
                    pytz.utc.localize(hr_attendance.check_in),
                    pytz.utc.localize(hr_attendance.check_out or default_check_out_dt),
                    hr_attendance,
                )
            )
        return WorkIntervals(intervals)

    def _get_hr_attendance_contract_intervals(self, start_dt, end_dt, only_lunch=False):
        # this is the same code as _get_attendance_intervals() from
        # hr_work_entry_contract, except that the work_entry_source value is
        # not checked, and there is an option to return only lunch break
        # intervals.
        employees_by_calendar = defaultdict(lambda: self.env["hr.employee"])
        for contract in self:
            employees_by_calendar[contract.resource_calendar_id] |= contract.employee_id
        result = dict()
        for calendar, employees in employees_by_calendar.items():
            result.update(
                calendar._attendance_intervals_batch(
                    start_dt,
                    end_dt,
                    resources=employees.resource_id,
                    tz=pytz.timezone(calendar.tz),
                    lunch=only_lunch,
                )
            )
        return result

    def _get_attendance_intervals(self, start_dt, end_dt):
        result = super()._get_attendance_intervals(start_dt, end_dt)
        contracts = self.filtered(lambda c: c.work_entry_source == "attendance_oca")
        lunch_contract_intervals = contracts._get_hr_attendance_contract_intervals(
            start_dt, end_dt, only_lunch=True
        )
        for contract in contracts:
            hr_attendances = contract._get_hr_attendances(start_dt, end_dt)
            hr_attendance_intervals = self._hr_attendances_to_work_intervals(
                hr_attendances
            )
            # difference with the attendances first return the attendance
            # intervals minus the lunch break intervals from the contracts, but
            # still linked to the hr.attendance record.
            resource_id = contract.employee_id.resource_id.id
            result[resource_id] = (
                hr_attendance_intervals - lunch_contract_intervals[resource_id]
            )
        return result

    def _get_interval_work_entry_type(self, interval):
        if self.work_entry_source == "attendance_oca":
            return self.env.company.attendance_hr_work_entry_type_id
        return super()._get_interval_work_entry_type(interval)

    def _get_more_vals_attendance_interval(self, interval):
        result = super()._get_more_vals_attendance_interval(interval)
        if self.work_entry_source == "attendance_oca":
            if interval[2]._name == "hr.attendance":
                result += [("attendance_id", interval[2].id)]
        return result
