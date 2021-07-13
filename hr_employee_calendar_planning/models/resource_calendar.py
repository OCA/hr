# Copyright 2019 Tecnativa - Pedro M. Baeza
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    active = fields.Boolean(default=True)

    @api.constrains("active")
    def _check_active(self):
        for item in self:
            total_items = self.env["hr.employee.calendar"].search_count(
                [("calendar_id", "=", item.id)]
            )
            if total_items:
                raise ValidationError(
                    _("%s is used in %s employee(s). You should change them first.")
                    % (item.name, total_items)
                )

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
