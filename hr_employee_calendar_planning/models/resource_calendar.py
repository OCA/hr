# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    active = fields.Boolean(
        default=True,
    )
    auto_generate = fields.Boolean()

    @api.multi
    def write(self, vals):
        res = super(ResourceCalendar, self).write(vals)
        if 'attendance_ids' not in vals:
            return res
        for record in self.filtered(lambda x: not x.auto_generate):
            calendars = self.env['hr.employee.calendar'].search([
                ('calendar_id', '=', record.id)
            ])
            for employee in calendars.mapped('employee_id'):
                employee._regenerate_calendar()
        return res
