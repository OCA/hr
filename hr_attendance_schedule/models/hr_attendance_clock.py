# -*- coding: utf-8 -*-
import pytz
from datetime import datetime

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

class AttendanceClock(models.Model):
    _name = 'hr_attendance_schedule.clock'
    _auto = False

    @api.model
    def get_system_clock(self):
        now = datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        return pytz.utc.localize(now).isoformat()
