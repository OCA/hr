# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Samuel Fringeli <samuel.fringeli@me.com>
#
#    The licence is in the file __manifest__.py
#
##############################################################################

from odoo import models, fields, api


class HrChangeDayRequest(models.Model):
    _name = 'hr.change.day.request'
    _inherit = 'mail.thread'
    _description = 'Change day request'

    name = fields.Char(compute='_compute_name', store=True)
    user_id = fields.Many2one('res.users', string='Manager',
                              track_visibility='onchange')

    day1_id = fields.Many2one('hr.forced.due.hours')
    day2_id = fields.Many2one('hr.forced.due.hours')
    employee_id = fields.Many2one('hr.employee', related='day1_id.employee_id')

    date1 = fields.Date('Date 1', related='day1_id.date')
    date2 = fields.Date('Date 2', related='day2_id.date')
    forced1 = fields.Float('Hours 1', related='day1_id.forced_due_hours')
    forced2 = fields.Float('Hours 2', related='day2_id.forced_due_hours')

    forced = fields.Char('Hours changed', compute='_compute_hours')

    @api.model
    def create(self, vals):
        if 'user_id' not in vals:
            manager = self.get_manager(vals['employee_id'])
            vals['user_id'] = manager.user_id.id if manager else 1  # admin

        forced_due_hours = self.env['hr.forced.due.hours']

        day1 = {
            'employee_id': vals['employee_id'],
            'date': vals['date1'],
            'forced_due_hours': vals['forced1']
        }
        day2 = {
            'employee_id': vals['employee_id'],
            'date': vals['date2'],
            'forced_due_hours': vals['forced2']
        }

        day1_id = forced_due_hours.create(day1)
        day2_id = forced_due_hours.create(day2)

        res = super(HrChangeDayRequest, self).create({
            'day1_id': day1_id.id,
            'day2_id': day2_id.id,
            'user_id': vals['user_id']
        })

        for d in [day1, day2]:
            forced_due_hours.recompute_due_hours(d['employee_id'], d['date'])

        return res

    @api.model
    def get_manager(self, employee_id):
        return self.env['hr.employee'].browse(employee_id).parent_id

    @api.multi
    def write(self, vals):
        if 'employee_id' in vals:
            manager = self.get_manager(vals['employee_id'])
            vals['user_id'] = manager.user_id.id if manager else 1  # admin

        return super(HrChangeDayRequest, self).write(vals)

    @api.multi
    def unlink(self):
        for request in self:
            request.day1_id.unlink()
            request.day2_id.unlink()

        super(HrChangeDayRequest, self).unlink()

    @api.multi
    def _compute_hours(self):
        for h in self:
            h.forced = h.forced2 if h.forced != 0 else h.forced1

    @api.multi
    @api.depends('employee_id', 'date1', 'date2', 'forced')
    def _compute_name(self):
        for h in self:
            h.name = u'{}, {}/{}, {} changed'\
                .format(h.employee_id.display_name, h.date1, h.date2,
                        self.env['hr.employee'].convert_hour_to_time(h.forced))
