# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Stephane Eicher <seicher@compassion.ch>
#    @author: Emanuel Cino <ecino@compassion.ch>
#
#    The licence is in the file __manifest__.py
#
##############################################################################
import logging

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    keep_due_hours = fields.Boolean(related='holiday_status_id.keep_due_hours')

    ##########################################################################
    #                               ORM METHODS                              #
    ##########################################################################
    @api.multi
    def action_validate(self):
        res = super(HrHolidays, self).action_validate()
        att_days = self.find_attendance_days()
        att_days.recompute_due_hours()
        return res

    @api.multi
    def action_refuse(self):
        res = super(HrHolidays, self).action_refuse()
        att_days = self.find_attendance_days()
        att_days.recompute_due_hours()
        return res

    ##########################################################################
    #                             PUBLIC METHODS                             #
    ##########################################################################
    @api.multi
    def find_attendance_days(self):
        att_days = self.env['hr.attendance.day']
        for rd in self:
            att_day = att_days.search([
                ('employee_id', '=', rd.employee_id.id),
                ('date', '>=', rd.date_from),
                ('date', '<=', rd.date_to)
            ])
            # Add leave in attendance day
            att_day.write({'leave_ids': [(4, rd.id)]})
            att_days |= att_day
        return att_days

    @api.multi
    def compute_leave_time(self, str_date):
        """
        Compute leave duration for the day.
        :param str_date: date to compute (string)
        :return: daily leave duration (in hours)
        :rtype: float [0:24]
        """

        start_time = fields.Datetime.from_string(self.date_from)
        end_time = fields.Datetime.from_string(self.date_to)
        start_day = fields.Date.from_string(self.date_from)
        end_day = fields.Date.from_string(self.date_to)

        date = fields.Date.from_string(str_date)

        if date == start_day == end_day:
            duration = (end_time - start_time).total_seconds() / 3600.0
        elif start_day < date < end_day:
            duration = 24
        elif start_day <= date <= end_day:
            if date == start_day or date == end_day:
                end_time = start_time.replace(hour=23, minute=59)
            else:
                start_time = end_time.replace(hour=0, minute=0)
            duration = (end_time - start_time).total_seconds() / 3600.0
        else:
            _logger.error(
                "This attendance day doesn't correspond to this leave"
            )
            duration = 0

        return duration
