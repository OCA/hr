import math
from datetime import timedelta

from odoo import fields, models


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    def _retrieve_day_matching_attendances(self, day):
        domain = [("calendar_id", "=", self.id), ("dayofweek", "=", day.weekday())]
        if self.two_weeks_calendar:
            # Employee has Even/Odd weekly calendar
            week_type = 1 if int(math.floor((day.toordinal() - 1) / 7) % 2) else 0
            domain.append(("week_type", "=", week_type))
        result = self.env["resource.calendar.attendance"].search(domain)
        return result

    def is_working_day(self, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        if len(day_attendances) == 0:
            # This day of the week is not supposed to be a working day
            return False
        else:
            # This day of the week is supposed to be a working day
            return True

    def is_full_working_day(self, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        morning_worked = (
            len(day_attendances.filtered(lambda x: x.day_period == "morning")) > 0
        )
        afternoon_worked = (
            len(day_attendances.filtered(lambda x: x.day_period == "afternoon")) > 0
        )
        return morning_worked and afternoon_worked

    def _is_worked_attendance(self, resource, day, attendance):
        attendance_start = fields.Datetime.to_datetime(day.date()) + timedelta(
            hours=attendance.hour_from
        )
        attendance_end = fields.Datetime.to_datetime(day.date()) + timedelta(
            hours=attendance.hour_to
        )
        resource_leaves = self.env["resource.calendar.leaves"].search(
            [
                ("resource_id", "=", resource.id),
                ("date_from", "<=", attendance_start),
                ("date_to", ">=", attendance_end),
            ]
        )
        if resource_leaves:
            return False
        else:
            # a part or the whole attendance is worked
            return True

    def is_worked_day(self, resource, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        # If at least one attendance is worked, return True
        for attendance in day_attendances:
            if self._is_worked_attendance(resource, day, attendance):
                return True
        return False

    def all_attendances_worked(self, resource, day):
        day_attendances = self._retrieve_day_matching_attendances(day)
        # If at least one attendance is not worked, return False
        for attendance in day_attendances:
            if not self._is_worked_attendance(resource, day, attendance):
                return False
        return True
