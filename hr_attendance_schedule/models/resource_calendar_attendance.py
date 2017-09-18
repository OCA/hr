# -*- coding: utf-8 -*-
from odoo import fields, models

from attendance_action import AttendanceAction


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    grace_before_checkin = fields.Float(help="Grace time before checkin in minutes")
    grace_after_checkin = fields.Float(help="Grace time after checkin in minutes")
    grace_before_checkout = fields.Float(help="Grace time before checkout in minutes")
    grace_after_checkout = fields.Float(help="Grace time after checkout in minutes")

    def get_action_date(self, in_out, employee_id):
        action = AttendanceAction(self, in_out, employee_id.resource_id)
        return action.get_action_date()
