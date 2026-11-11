# Copyright 2026 Tecnativa - Juan Carlos Oñate
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeCalendarWizard(models.TransientModel):
    _name = "hr.employee.calendar.wizard"
    _description = "Plan a working time for several employees"

    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Employees",
        required=True,
        default=lambda self: self.env.context.get("active_ids"),
    )
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
    )
    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        if any(w.date_end < w.date_start for w in self):
            raise ValidationError(
                self.env._("Date end should be higher than date start")
            )

    def action_apply(self):
        for employee in self.employee_ids:
            employee._plan_calendar(self.calendar_id, self.date_start, self.date_end)
