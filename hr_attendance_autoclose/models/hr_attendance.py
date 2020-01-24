# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import timedelta


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    @api.multi
    @api.depends('check_out', 'check_in')
    def _compute_open_worked_hours(self):
        for attendance in self:
            if attendance.check_out:
                delta = datetime.strptime(
                    attendance.check_out,
                    DEFAULT_SERVER_DATETIME_FORMAT) - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                open_worked_hours = delta.total_seconds() / 3600.0
            else:
                delta = datetime.now() - datetime.strptime(
                    attendance.check_in, DEFAULT_SERVER_DATETIME_FORMAT)
                open_worked_hours = delta.total_seconds() / 3600.0
            attendance.open_worked_hours = open_worked_hours
        return True

    open_worked_hours = fields.Float(
        string='Worked hours', compute='_compute_open_worked_hours',
    )

    @api.multi
    def autoclose_attendance(self, reason):
        self.ensure_one()
        max_hours = self.employee_id.get_max_hours_per_day()
        leave_time = datetime.strptime(
            self.check_in, DEFAULT_SERVER_DATETIME_FORMAT
        ) + timedelta(hours=max_hours)
        vals = {'check_out': leave_time.strftime(
            DEFAULT_SERVER_DATETIME_FORMAT)}
        if reason:
            vals['attendance_reason_ids'] = [(4, reason.id)]
        self.write(vals)

    @api.multi
    def needs_autoclose(self):
        self.ensure_one()
        max_hours = self.employee_id.get_max_hours_per_day()
        close = not self.employee_id.no_autoclose
        return close and max_hours and self.open_worked_hours > max_hours

    @api.model
    def check_for_incomplete_attendances(self):
        stale_attendances = self.search(
            [('check_out', '=', False)])
        reason = self.env['hr.attendance.reason'].search(
            [('code', '=', 'S-CO')], limit=1)
        for att in stale_attendances.filtered(lambda a: a.needs_autoclose()):
            att.autoclose_attendance(reason)

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ If this is an automatic checkout the constraint is invalid
        as there may be old attendances not closed
        """
        reason = self.env['hr.attendance.reason'].search(
            [('code', '=', 'S-CO')], limit=1)
        if not reason:
            return super(HrAttendance, self)._check_validity()
        if self.filtered(lambda att:
                         att.attendance_reason_ids and reason
                         in att.attendance_reason_ids):
            return True
        return super(HrAttendance, self)._check_validity()
