# Copyright 2025- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import pytz

from odoo import api, fields, models


class HrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    timesheet_duration = fields.Float(compute="_compute_timesheet_duration", store=True)
    is_hatched = fields.Boolean(
        compute="_compute_timesheet_conflict",
        string="Timesheet Conflict",
        store=True,
        readonly=False,
    )

    @api.depends("date_start", "employee_id")
    def _compute_timesheet_duration(self):
        if not self:
            return
        min_datetime = min(self.mapped("date_start"))
        max_datetime = max(self.mapped("date_stop"))
        dates = self.mapped(
            lambda work_entry: pytz.UTC.localize(work_entry.date_start)
            .astimezone(pytz.timezone(work_entry.employee_id.tz))
            .replace(tzinfo=None)
            .date()
        )
        min_date = min(dates)
        max_date = max(dates)
        employee_ids = self.mapped("employee_id").ids
        timesheets = (
            self.env["account.analytic.line"]
            .with_context(tz="UTC")
            .read_group(
                domain=[
                    ("project_id", "!=", False),
                    ("employee_id", "in", employee_ids),
                    ("date", ">=", min_date),
                    ("date", "<=", max_date),
                ],
                fields=["unit_amount"],
                groupby=["employee_id", "date:day"],
                lazy=False,
            )
        )
        timesheet_dict = {eid: {} for eid in employee_ids}
        for line in timesheets:
            date = fields.Date().from_string(line["__range"]["date:day"]["from"])
            timesheet_dict[line["employee_id"][0]][date] = line["unit_amount"]
        work_entries_dict = {eid: {} for eid in employee_ids}
        for employee_id in employee_ids:
            employee = self.env["hr.employee"].browse(employee_id)
            work_entries = (
                self.env["hr.work.entry"]
                .with_context(tz=employee.tz)
                .read_group(
                    domain=[
                        ("employee_id", "=", employee_id),
                        ("date_start", ">=", min_datetime),
                        ("date_stop", "<=", max_datetime),
                    ],
                    fields=[],
                    groupby=["date_start:day"],
                )
            )
            work_entries_dict[employee_id] = {
                pytz.UTC.localize(
                    fields.Datetime().from_string(
                        line["__range"]["date_start:day"]["from"]
                    )
                )
                .astimezone(pytz.timezone(employee.tz))
                .replace(tzinfo=None)
                .date(): line["date_start_count"]
                for line in work_entries
            }
        for work_entry in self:
            date_start = (
                pytz.UTC.localize(work_entry.date_start)
                .astimezone(pytz.timezone(work_entry.employee_id.tz))
                .replace(tzinfo=None)
                .date()
            )
            timesheet_duration = timesheet_dict[work_entry.employee_id.id].get(
                date_start, 0.0
            )
            work_entry_count = work_entries_dict[work_entry.employee_id.id].get(
                date_start, 0
            )
            work_entry.timesheet_duration = (
                timesheet_duration / work_entry_count if work_entry_count else 0.0
            )

    @api.depends("duration", "timesheet_duration")
    def _compute_timesheet_conflict(self):
        for entry in self:
            entry.is_hatched = entry.duration > 0.0 and (
                entry.timesheet_duration == 0.0
                or entry.timesheet_duration > entry.duration
            )
