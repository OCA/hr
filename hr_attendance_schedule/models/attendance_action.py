# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AttendanceAction(object):
    def __init__(self, attendance_id, in_out, resource_id):
        self._attendance_id = attendance_id
        self._in_out = in_out
        self._resource_id = resource_id
        self._now = fields.Datetime.from_string(fields.Datetime.now())
        d_day = self._create_datetime_from_dayofweek()
        self._start_datetime = d_day + timedelta(hours=attendance_id.hour_from)
        self._end_datetime = d_day + timedelta(hours=attendance_id.hour_to)
        if self._end_datetime <= self._start_datetime:
            self._end_datetime += timedelta(days=1)

    def get_action_date(self):
        if self._is_now_allowed():
            matching_date = self._get_matching_date()
            if matching_date:
                if self._in_out == 'in':
                    offset = matching_date - self._start_datetime
                else:
                    offset = matching_date - self._end_datetime
                action_date = datetime.strftime(self._now - offset, DEFAULT_SERVER_DATETIME_FORMAT)
                return action_date, False
        return None, True

    def _is_now_allowed(self):
        is_after_from = not self._attendance_id.date_from or fields.Date.from_string(self._attendance_id.date_from) <= self._now.date()
        is_before_to = not self._attendance_id.date_to or fields.Date.from_string(self._attendance_id.date_to) >= self._now.date()
        return is_after_from and is_before_to and not self._is_now_in_leave()

    def _is_now_in_leave(self):
        calendar_leaves_matches = (l.matches(self._now) for l in self._attendance_id.calendar_id.leave_ids if not l.resource_id)
        employee_leaves_matches = (l.matches(self._now) for l in self._resource_id.leave_ids)
        return any(calendar_leaves_matches) or any(employee_leaves_matches)

    def _get_matching_date(self):
        lower, upper = self._get_span()
        delta_days = upper.date() - lower.date()
        dates_in_delta = [lower + timedelta(days=i) for i in range(delta_days.days + 1)]
        matching_date_gen = (datetime.combine(d.date(), self._now.time()) for d in dates_in_delta if d.weekday() == self._now.weekday())
        matching_datetime_gen = (dt for dt in matching_date_gen if lower <= dt <= upper)
        return next(matching_datetime_gen, None)

    def _get_span(self):
        if self._in_out == 'in':
            lower = self._start_datetime - timedelta(minutes=self._attendance_id.grace_before_checkin)
            upper = self._start_datetime + timedelta(minutes=self._attendance_id.grace_after_checkin)
        else:
            lower = self._end_datetime - timedelta(minutes=self._attendance_id.grace_before_checkout)
            upper = self._end_datetime + timedelta(minutes=self._attendance_id.grace_after_checkout)
        return lower, upper

    def _create_datetime_from_dayofweek(self):
        some_monday = datetime(2017, 1, 2)
        return some_monday + timedelta(days=int(self._attendance_id.dayofweek))
