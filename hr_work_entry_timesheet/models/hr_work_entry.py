# Copyright 2025- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrWorkEntry(models.Model):
    _inherit = "hr.work.entry"

    timesheet_duration = fields.Float(compute="_compute_timesheet_duration", store=True)
    timesheet_conflict = fields.Boolean(
        compute="_compute_timesheet_conflict", store=True, readonly=False
    )
    is_hatched = fields.Boolean(related="timesheet_conflict")

    @api.depends("date_start", "employee_id")
    def _compute_timesheet_duration(self):
        if not self:
            return
        timesheets = self.env["account.analytic.line"].read_group(
            domain=[
                ("project_id", "!=", False),
                ("employee_id", "in", self.mapped("employee_id").ids),
                ("date", ">=", min(self.mapped("date_start")).date()),
                ("date", "<=", max(self.mapped("date_start")).date()),
            ],
            fields=["unit_amount"],
            groupby=["employee_id", "date:day"],
            lazy=False,
        )
        result = {eid: {} for eid in self.mapped("employee_id").ids}
        for line in timesheets:
            date = fields.Date().from_string(line["__range"]["date:day"]["from"])
            result[line["employee_id"][0]][date] = line["unit_amount"]
        for work_entry in self:
            work_entry.timesheet_duration = result[work_entry.employee_id.id].get(
                work_entry.date_start.date(), 0.0
            )

    @api.depends("duration", "timesheet_duration")
    def _compute_timesheet_conflict(self):
        for entry in self:
            entry.timesheet_conflict = entry.duration > 0.0 and (
                entry.timesheet_duration == 0.0
                or entry.timesheet_duration > entry.duration * 2
            )
