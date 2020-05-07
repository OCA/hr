# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    active = fields.Boolean(default=True)

    def write(self, vals):
        res = super(ResourceCalendar, self).write(vals)
        if "attendance_ids" in vals:
            for record in self.filtered("active"):
                calendars = self.env["hr.employee.calendar"].search(
                    [("calendar_id", "=", record.id)]
                )
                for employee in calendars.mapped("employee_id"):
                    employee._regenerate_calendar()
        return res
