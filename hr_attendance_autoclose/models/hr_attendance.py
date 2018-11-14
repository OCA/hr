# -*- coding: utf-8 -*-
# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.multi
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = datetime.strptime(
                    attendance.check_out,
                    DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                worked_hours = delta.total_seconds() / 3600.0
            else:
                delta = datetime.now() - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                worked_hours = delta.total_seconds() / 3600.0
            attendance.worked_hours = worked_hours
        return True

    worked_hours = fields.Float(
        string='Worked hours', compute='_compute_worked_hours', store=False)

    @api.model
    def check_for_incomplete_attendances(self):
        stale_attendances = self.search(
            [('check_out', '=', False)])
        reason = self.env['hr.attendance.reason'].search(
            [('code', '=', 'S-CO')], limit=1)
        for att in stale_attendances:
            max_hours = att.employee_id.company_id.\
                attendance_maximum_hours_per_day
            if max_hours:
                leave_time = datetime.strptime(
                    att.check_in, DEFAULT_SERVER_DATETIME_FORMAT) + timedelta(
                    hours=max_hours)
                if reason:
                    vals = {'check_out': leave_time.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT),
                        'attendance_reason_id': [(4, reason.id)]}
                else:
                    vals = {'check_out': leave_time.strftime(
                        DEFAULT_SERVER_DATETIME_FORMAT)}
                att.write(vals)
