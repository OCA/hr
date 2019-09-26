# -*- coding: utf-8 -*-
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    calendar_ids = fields.One2many(
        comodel_name="hr.employee.calendar",
        inverse_name="employee_id",
        string="Calendar planning",
    )

    def _regenerate_calendar(self):
        self.ensure_one()
        if not self.calendar_id or self.calendar_id.active:
            self.calendar_id = self.env['resource.calendar'].create({
                'active': False,
                'name': _(
                    'Auto generated calendar for employee'
                ) + ' %s' % self.id,
            }).id
        else:
            self.calendar_id.attendance_ids.unlink()
        vals_list = []
        for line in self.calendar_ids:
            for calendar_line in line.calendar_id.attendance_ids:
                vals_list.append((0, 0, {
                    'name': calendar_line.name,
                    'dayofweek': calendar_line.dayofweek,
                    'hour_from': calendar_line.hour_from,
                    'hour_to': calendar_line.hour_to,
                    'date_from': line.date_start,
                    'date_to': line.date_end,
                }))
        self.calendar_id.attendance_ids = vals_list


class HrEmployeeCalendar(models.Model):
    _name = 'hr.employee.calendar'

    date_start = fields.Date(
        string="Start",
    )
    date_end = fields.Date(
        string="End",
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
    )
    calendar_id = fields.Many2one(
        comodel_name="resource.calendar",
        string="Working Time",
        required=True,
    )

    _sql_constraints = [
        ('date_consistency',
         'CHECK(date_start <= date_end)',
         'Date end should be higher than date start'),
    ]

    def create(self, vals):
        record = super(HrEmployeeCalendar, self).create(vals)
        record.employee_id._regenerate_calendar()
        return record

    def write(self, vals):
        res = super(HrEmployeeCalendar, self).write(vals)
        for employee in self.mapped('employee_id'):
            employee._regenerate_calendar()
        return res
