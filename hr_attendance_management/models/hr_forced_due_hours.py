# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class HrForcedDueHours(models.Model):
    _name = 'hr.forced.due.hours'
    _description = "HR forced due hours"
    _order = 'date'

    _sql_constraints = [('unique_due_hours', 'unique(date, employee_id)',
                         'This "Forced due hour" already exists')]

    employee_id = fields.Many2one('hr.employee',
                                  string='Employee', required=True)
    date = fields.Date('Date', required=True)
    forced_due_hours = fields.Float('Forced due hours', required=True)

    @api.model
    def recompute_due_hours(self, employee_id, date):
        return self.env['hr.attendance.day'].search(
            [('employee_id', '=', employee_id),
             ('date', '=', date)]).recompute_due_hours()

    @api.multi
    def write(self, vals):
        for record in self:
            old_vals = dict()
            for field in ['employee_id', 'date', 'forced_due_hours']:
                old_vals[field] = getattr(record, field)

            super(HrForcedDueHours, record).write(vals)

            record.recompute_due_hours(
                old_vals['employee_id'].id, old_vals['date'])
            record.recompute_due_hours(record.employee_id.id, record.date)

    @api.multi
    def unlink(self):
        employee_ids = self.mapped('employee_id.id')
        dates = self.mapped('date')

        super(HrForcedDueHours, self).unlink()
        for i in range(len(employee_ids)):
            self.recompute_due_hours(employee_ids[i], dates[i])
