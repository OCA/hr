# -*- coding: utf-8 -*-
# Copyright (C) 2018 Compassion CH
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    attendance_day_ids = fields.Many2many('hr.attendance.day', store=True,
                                          string='Attendances days',
                                          compute='_compute_att_day')

    ##########################################################################
    #                             PUBLIC METHODS                             #
    ##########################################################################
    @api.depends('date_from', 'date_to', 'state')
    @api.multi
    def _compute_att_day(self):
        att_days = self.env['hr.attendance.day']
        for rd in self:
            # Remove the current leave from the attendance_day.leave_ids in
            # case of the date change
            for att in rd.attendance_day_ids:
                if self in att.leave_ids:
                    att.leave_ids = att.leave_ids.filtered(
                        lambda r: r.id != rd.id)

            att_days = att_days.search([
                ('employee_id', '=', rd.employee_id.id),
                ('date', '>=', rd.date_from),
                ('date', '<=', rd.date_to)
            ])

            rd.attendance_day_ids = att_days

            for att_day in att_days:
                att_day.leave_ids = att_day.leave_ids | self
