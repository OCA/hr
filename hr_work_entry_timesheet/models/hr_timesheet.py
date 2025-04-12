# Copyright 2025- Le Filament (https://le-filament.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from dateutil.relativedelta import relativedelta

from odoo import api, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _get_work_entry(self):
        work_entries = self.env["hr.work.entry"]
        for timesheet in self.filtered(
            lambda line: line.project_id and line.employee_id
        ):
            work_entries += work_entries.search(
                [
                    ("employee_id", "=", timesheet.employee_id.id),
                    ("date_start", ">=", timesheet.date),
                    ("date_start", "<", timesheet.date + relativedelta(days=1)),
                ]
            )
        return work_entries

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        timesheets = res.filtered("project_id")
        if not timesheets:
            return res
        work_entries = timesheets._get_work_entry()
        if work_entries:
            work_entries._compute_timesheet_duration()
        return res

    def write(self, vals):
        res = super().write(vals)
        if ("unit_amount" in vals or "employee_id" in vals or "date" in vals) and (
            self.filtered("project_id") or "project_id" in vals
        ):
            self._get_work_entry()._compute_timesheet_duration()
        return res

    def unlink(self):
        work_entries = self.env["hr.work.entry"]
        timesheets = self.filtered("project_id")
        if timesheets:
            work_entries = timesheets._get_work_entry()
        res = super().unlink()
        if timesheets:
            work_entries._compute_timesheet_duration()
        return res
