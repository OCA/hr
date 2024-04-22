# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import calendar
from datetime import timedelta
from itertools import product as iter_cartesian

from odoo import fields, models


class TimesheetPrefill(models.TransientModel):
    """
    Wizard used to prefill timesheets
    """

    _name = "timesheet.prefill"
    _description = "Timesheet prefill"

    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Employees",
        required=True,
    )
    project_ids = fields.Many2many(
        comodel_name="project.project",
        string="Projects",
        required=True,
    )
    date_from = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(day=1),
    )
    date_to = fields.Date(
        required=True,
        default=lambda self: fields.Date.context_today(self).replace(
            day=calendar.monthrange(
                fields.Date.context_today(self).year,
                fields.Date.context_today(self).month,
            )[1]
        ),
    )

    def action_generate(self):
        timesheet_lines = self._action_generate()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_timesheet.timesheet_action_all"
        )
        action.update(
            {
                "domain": [("id", "in", timesheet_lines.ids)],
            }
        )
        return action

    def _date_range_list(self):
        # Return generator for a list datetime.date objects (inclusive) between
        # start_date and end_date (inclusive).
        # Use min/max to fix the order
        start_date, end_date = min([self.date_from, self.date_to]), max(
            [self.date_from, self.date_to]
        )
        curr_date = start_date
        while curr_date <= end_date:
            yield curr_date
            curr_date += timedelta(days=1)

    def _action_generate(self):
        timesheet_lines_values = []
        for date, employee, project in iter_cartesian(
            self._date_range_list(), self.employee_ids, self.project_ids
        ):
            timesheet_lines_values.append(
                {
                    "employee_id": employee.id,
                    "project_id": project.id,
                    "date": date,
                }
            )
        return self.env["account.analytic.line"].create(timesheet_lines_values)
