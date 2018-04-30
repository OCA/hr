# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2016 Open Net Sarl (https://www.open-net.ch)
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Eicher Stephane <seicher@compassion.ch>
#    @author: Coninckx David <david@coninckx.com>
#
#    The licence is in the file __manifest__.py
#
##############################################################################


import logging

from datetime import date

from odoo import api, models, fields

_logger = logging.getLogger(__name__)


class ResCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    due_hours = fields.Float()

    @api.model
    def create(self, vals):
        # Update attendance days of employees that are using the schedule
        res = super(ResCalendarAttendance, self).create(vals)
        calendar = res.calendar_id
        date_from = res.date_from or date.min
        date_to = res.date_to or date.max
        contracts = self.env['hr.contract'].search([
            ('working_hours', '=', calendar.id),
            ('date_start', '>=', date_from),
            '|', ('date_end', '<=', date_to), ('date_end', '=', False)
        ])
        employees = contracts.mapped('employee_id')
        employees |= employees.search([
            ('calendar_id', '=', calendar.id)
        ])
        attendance_days = self.env['hr.attendance.day'].search([
            ('employee_id', 'in', employees.ids),
            ('date', '>=', date_from),
            ('date', '<=', date_to)
        ])
        attendance_days.update_calendar_attendance()
        attendance_days.update_extra_hours_lost()
        return res
