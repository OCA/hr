from odoo import fields, models

from datetime import datetime, timedelta

import pytz


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    grace_before_checkin = fields.Float(
        help="Grace time before checkin in minutes")
    grace_after_checkin = fields.Float(
        help="Grace time after checkin in minutes")
    grace_before_checkout = fields.Float(
        help="Grace time before checkout in minutes")
    grace_after_checkout = fields.Float(
        help="Grace time after checkout in minutes")

    def get_action_date(self, in_out, employee_id):
        now = fields.Datetime.from_string(fields.Datetime.now())
        if self._is_now_allowed(now, employee_id):
            start_datetime, end_datetime = self._get_start_and_end_datetimes()
            matching_date = self._get_matching_date(in_out, now,
                                                    start_datetime,
                                                    end_datetime)
            if matching_date:
                if in_out == 'in':
                    offset = matching_date - start_datetime
                else:
                    offset = matching_date - end_datetime
                return now - offset, False
        return None, True

    def _get_start_and_end_datetimes(self):
        d_day = self._create_datetime_from_dayofweek()
        start = d_day + timedelta(hours=self.hour_from)
        end = d_day + timedelta(hours=self.hour_to)
        if end <= start:
            end += timedelta(days=1)
        utc_start = self._convert_attendance_dt_to_utc_dt(start)
        utc_end = self._convert_attendance_dt_to_utc_dt(end)
        return utc_start, utc_end

    def _convert_attendance_dt_to_utc_dt(self, dt):
        """We consider OdooBot's timezone to be the system timezone"""
        local_dt = pytz.timezone(self.sudo().env.user.tz).localize(dt)
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)

    def _create_datetime_from_dayofweek(self):
        now = fields.Datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        monday_this_week = now - timedelta(days=now.weekday())
        return monday_this_week + timedelta(days=int(self.dayofweek))

    def _is_now_allowed(self, now, employee_id):
        is_after_from = not self.date_from or \
                        fields.Date.from_string(self.date_from) <= now.date()
        is_before_to = not self.date_to or \
                       fields.Date.from_string(self.date_to) >= now.date()
        return is_after_from and \
               is_before_to and \
               not self._is_now_in_leave(now, employee_id)

    def _is_now_in_leave(self, now, employee_id):
        calendar_leaves_matches = (l.matches(now)
                                   for l in self.calendar_id.leave_ids
                                   if not l.resource_id)
        employee_leaves_matches = (l.matches(now)
                                   for l in employee_id.resource_id.leave_ids)
        return any(calendar_leaves_matches) or any(employee_leaves_matches)

    def _get_matching_date(self, in_out, now, start, end):
        lower, upper = self._get_span(in_out, start, end)
        delta_days = upper.date() - lower.date()
        dates_in_delta = [lower + timedelta(days=i)
                          for i in range(delta_days.days + 1)]
        matching_date_gen = (datetime.combine(d.date(), now.time())
                             for d in dates_in_delta
                             if d.weekday() == now.weekday())
        matching_datetime_gen = (dt for dt in matching_date_gen
                                 if lower <= dt <= upper)
        return next(matching_datetime_gen, None)

    def _get_span(self, in_out, start, end):
        if in_out == 'in':
            lower = start - timedelta(minutes=self.grace_before_checkin)
            upper = start + timedelta(minutes=self.grace_after_checkin)
        else:
            lower = end - timedelta(minutes=self.grace_before_checkout)
            upper = end + timedelta(minutes=self.grace_after_checkout)
        return lower, upper
