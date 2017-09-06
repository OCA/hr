# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class Period(models.Model):
    _name = 'hr_attendance_schedule.period'

    schedule_id = fields.Many2one('hr_attendance_schedule.schedule', required=True, ondelete='cascade')
    active = fields.Boolean(default=True)
    duration = fields.Float("Duration (h)", required=True)
    start_datetime = fields.Datetime()
    grace_before_checkin = fields.Float(help="Grace time before checkin in minutes")
    grace_after_checkin = fields.Float(help="Grace time after checkin in minutes")
    grace_before_checkout = fields.Float(help="Grace time before checkout in minutes")
    grace_after_checkout = fields.Float(help="Grace time after checkout in minutes")

    @api.multi
    def compute_week_day(self):
        week_days = [
            _("Monday"),
            _("Tuesday"),
            _("Wednesday"),
            _("Thursday"),
            _("Friday"),
            _("Saturday"),
            _("Sunday")
        ]
        for period in self:
            start_datetime = self._parse_datetime(period.start_datetime)
            period.week_day = week_days[start_datetime.weekday()]

    week_day = fields.Char(compute=compute_week_day)

    def get_action_date(self, in_out):
        lower, upper = self._get_span(in_out)
        delta_days = upper.date() - lower.date()
        dates_in_delta = [lower + timedelta(days=i) for i in range(delta_days.days + 1)]
        now = self._parse_datetime(fields.Datetime.now())
        matching_date_gen = (datetime.combine(d.date(), now.time()) for d in dates_in_delta if d.weekday() == now.weekday())
        matching_datetime_gen = (dt for dt in matching_date_gen if lower <= dt <= upper)
        matching_date = next(matching_datetime_gen, None)
        if matching_date:
            in_out_date = self._parse_datetime(self.start_datetime)
            if in_out == 'out':
                in_out_date += timedelta(hours=self.duration)
            offset = matching_date - in_out_date
            return now - offset, False
        else:
            return None, True

    def _parse_datetime(self, string_value):
        return datetime.strptime(string_value, DEFAULT_SERVER_DATETIME_FORMAT)

    def _get_span(self, in_out):
        start_datetime = self._parse_datetime(self.start_datetime)
        if in_out == 'in':
            lower = start_datetime - timedelta(minutes=self.grace_before_checkin)
            upper = start_datetime + timedelta(minutes=self.grace_after_checkin)
        else:
            stop = start_datetime + timedelta(hours=self.duration)
            lower = stop - timedelta(minutes=self.grace_before_checkout)
            upper = stop + timedelta(minutes=self.grace_after_checkout)
        return lower, upper
