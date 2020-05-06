# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, models
from odoo.exceptions import UserError


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    @api.multi
    def write(self, vals):
        for attendance in self:
            lockdate = None
            if attendance.employee_id.attendance_lock_date:
                lockdate = attendance.employee_id.attendance_lock_date

            if lockdate:
                checkin = vals.get('check_in')
                if attendance.check_in < lockdate:
                    raise UserError(
                        _("You can't modify a validated attendance")
                    )
                if checkin and checkin < lockdate:
                    raise UserError(
                        _(
                            "You can't move a attendance in an "
                            "already validated week/TS"
                        )
                    )
        return super().write(vals)

    @api.multi
    def unlink(self):
        for attendance in self:
            lockdate = None
            if attendance.employee_id.attendance_lock_date:
                lockdate = attendance.employee_id.attendance_lock_date

            if lockdate and attendance.check_in < lockdate:
                raise UserError(_("You can't delete approved attendances"))
        return super().unlink()

    @api.model
    def create(self, vals):
        employee = self.env['hr.employee'].browse(vals['employee_id'])
        if employee.attendance_lock_date:
            lockdate = employee.attendance_lock_date
            if vals.get('check_in') < lockdate:
                raise UserError(
                    _("You can't create an attendance in a validated week/TS")
                )
        return super().create(vals)
