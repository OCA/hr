# Copyright 2020 Pavlov Media
# License LGPL-3 - See http://www.gnu.org/licenses/lgpl-3.0.html

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, \
    DEFAULT_SERVER_DATE_FORMAT

import pytz
from datetime import datetime, timedelta, time
from odoo.exceptions import ValidationError


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    split_attendance = fields.Boolean(
        string="Split Attendance",
        help="If attendance was split due to overnight coverage.")
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        related="employee_id.company_id", store=True)
    related_attendance_id = fields.Many2one('hr.attendance',
                                            string='Related Attendance')

    @api.model
    def create(self, vals):
        """ Prevent overnight attendance during creation"""
        if vals.get('check_out', False):
            employee = self.env['hr.employee'].browse(vals.get('employee_id'))
            check_in_date = pytz.utc.localize(datetime.strptime(
                vals.get('check_in'), '%Y-%m-%d %H:%M:%S')).astimezone(
                pytz.timezone(employee.tz)).date()
            check_out_date = pytz.utc.localize(datetime.strptime(
                vals.get('check_out'), '%Y-%m-%d %H:%M:%S')).astimezone(
                pytz.timezone(employee.tz)).date()
            if employee.company_id.split_attendance and \
                    check_in_date != check_out_date:
                raise ValidationError(_("Cannot create attendance that "
                                        "starts and ends on different days."))
        return super().create(vals)

    @api.multi
    def write(self, vals):
        """ If the user clocks out after midnight, then it will split the
        attendance at midnight of the employees timezone."""
        if 'check_out' in vals:
            check_in_date = pytz.utc.localize(
                self.check_in).astimezone(pytz.timezone(
                    self.employee_id.tz)).date()
            # Need to know if check_out is string or not because it
            # differs if updated via form vs kiosk modes.
            if not isinstance(vals.get('check_out'), str):
                check_out_date = pytz.utc.localize(
                    vals.get('check_out')).astimezone(pytz.timezone(
                        self.employee_id.tz)).date()
            if isinstance(vals.get('check_out'), str):
                check_out_date = pytz.utc.localize(
                    datetime.strptime(
                        vals.get('check_out'),
                        DEFAULT_SERVER_DATETIME_FORMAT)).astimezone(
                    pytz.timezone(
                        self.employee_id.tz)).date()
            if self.employee_id.company_id.split_attendance and \
                    check_in_date != check_out_date and \
                    not self.split_attendance:
                tz = pytz.timezone(self.employee_id.tz)
                current_check_out = tz.localize(
                    datetime.combine(datetime.strptime(
                        str(check_in_date),
                        DEFAULT_SERVER_DATE_FORMAT),
                        time(23, 59, 59))).astimezone(pytz.utc)
                new_check_in = tz.localize(
                    datetime.combine(datetime.strptime(
                        str(pytz.utc.localize(self.check_in).astimezone(
                            pytz.timezone(self.employee_id.tz)).date() +
                            timedelta(days=1)),
                        DEFAULT_SERVER_DATE_FORMAT),
                        time(0, 0, 0))).astimezone(pytz.utc)
                new_check_out = vals.get('check_out')
                vals['check_out'] = current_check_out.replace(tzinfo=None)
                vals['split_attendance'] = True
                res = super().write(vals)
                new_attendance = self.env['hr.attendance'].sudo().create({
                    'employee_id': self.employee_id.id,
                    'check_in': new_check_in,
                    'related_attendance_id': self.id,
                    'split_attendance': False})
                self.write({'related_attendance_id': new_attendance.id})
                new_attendance.write({'check_out': new_check_out})
            else:
                res = super().write(vals)
        else:
            res = super().write(vals)
        return res
