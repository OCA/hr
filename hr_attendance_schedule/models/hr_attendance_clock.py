import pytz

from odoo import api, fields, models


class AttendanceClock(models.AbstractModel):
    _name = 'hr_attendance_schedule.clock'
    _description = 'Attendance Clock'

    @api.model
    def get_system_clock(self):
        now = fields.Datetime.from_string(fields.Datetime.now())
        return pytz.utc.localize(now).isoformat()
