# -*- coding: utf-8 -*-
import pytz

from odoo import api, fields, models


class AttendanceClock(models.AbstractModel):
    _name = 'hr_attendance_schedule.clock'

    @api.model
    def get_system_clock(self):
        now = fields.Datetime.from_string(fields.Datetime.now())
        return pytz.utc.localize(now).isoformat()
