# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


class ResourceCalendarAttendance(models.Model):
    _inherit = 'resource.calendar.attendance'

    grace_before_checkin = fields.Float(help="Grace time before checkin in minutes")
    grace_after_checkin = fields.Float(help="Grace time after checkin in minutes")
    grace_before_checkout = fields.Float(help="Grace time before checkout in minutes")
    grace_after_checkout = fields.Float(help="Grace time after checkout in minutes")

    def get_action_date(self, in_out, employee_id):
        self._init_datetimes()
        if self._is_now_allowed(employee_id):
            matching_date = self._get_matching_date(in_out)
            if matching_date:
                offset = matching_date - (self._start_datetime if in_out == 'in' else self._end_datetime)
                return self._now - offset, False
        return None, True

    def _init_datetimes(self):
        self._now = datetime.strptime(fields.Datetime.now(), DEFAULT_SERVER_DATETIME_FORMAT)
        d_day = self._get_next_weekday(int(self.dayofweek))
        self._start_datetime = d_day + timedelta(hours=self.hour_from)
        self._end_datetime = d_day + timedelta(hours=self.hour_to)
        if self._end_datetime <= self._start_datetime:
            self._end_datetime += timedelta(days=1)

    def _is_now_allowed(self, employee_id):
        parse_date = lambda d: datetime.strptime(d, DEFAULT_SERVER_DATE_FORMAT).date()
        is_after_from = not self.date_from or parse_date(self.date_from) <= self._now.date()
        is_before_to = not self.date_to or parse_date(self.date_to) >= self._now.date()
        return is_after_from and is_before_to and not self._is_now_in_leave(employee_id)

    def _is_now_in_leave(self, employee_id):
        calendar_leaves_matches = (l.matches(self._now) for l in self.calendar_id.leave_ids if not l.resource_id)
        employee_leaves_matches = (l.matches(self._now) for l in employee_id.resource_id.leave_ids)
        return any(calendar_leaves_matches) or any(employee_leaves_matches)

    def _get_matching_date(self, in_out):
        lower, upper = self._get_span(in_out)
        delta_days = upper.date() - lower.date()
        dates_in_delta = [lower + timedelta(days=i) for i in range(delta_days.days + 1)]
        matching_date_gen = (datetime.combine(d.date(), self._now.time()) for d in dates_in_delta if d.weekday() == self._now.weekday())
        matching_datetime_gen = (dt for dt in matching_date_gen if lower <= dt <= upper)
        return next(matching_datetime_gen, None)

    def _get_span(self, in_out):
        if in_out == 'in':
            lower = self._start_datetime - timedelta(minutes=self.grace_before_checkin)
            upper = self._start_datetime + timedelta(minutes=self.grace_after_checkin)
        else:
            lower = self._end_datetime - timedelta(minutes=self.grace_before_checkout)
            upper = self._end_datetime + timedelta(minutes=self.grace_after_checkout)
        return lower, upper

    def _get_next_weekday(self, weekday):
        monday = datetime(2017, 1, 2)
        return monday + timedelta(days=weekday)
