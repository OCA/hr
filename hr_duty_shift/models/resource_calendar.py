# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from datetime import datetime
import pytz


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def get_duty_shift_domain(self, start, end):
        """
        returns the domain of the duties that cross whith a range. It should be
        the duties that begins before the range ends and ends after the range
        starts
        :param start: datetime
        :param end: datetime
        :return: a domain
        """
        return [
            ('employee_id', '=', self.env.context.get('employee_id')),
            ('start_date', '<=', fields.Datetime.to_string(end)),
            ('end_date', '>=', fields.Datetime.to_string(start)),
        ]

    def _iter_day_attendance_intervals(self, day_date, start_time, end_time):
        yield from super()._iter_day_attendance_intervals(
            day_date, start_time, end_time)
        if self.env.context.get('employee_id', False):
            tz = pytz.timezone(
                self.env.user.tz
            ) if self.env.user.tz else pytz.UTC
            datetime_start = tz.localize(
                datetime.combine(day_date, start_time).replace(tzinfo=None),
                is_dst=False
            ).astimezone(pytz.UTC).replace(tzinfo=None)
            datetime_end = tz.localize(
                datetime.combine(day_date, end_time).replace(tzinfo=None),
                is_dst=False
            ).astimezone(pytz.UTC).replace(tzinfo=None)
            shifts = self.env['hr.duty.shift'].search(
                self.get_duty_shift_domain(datetime_start, datetime_end))
            # The affected shifts are added as new intervals.
            for shift in shifts:
                dt_f = max(
                    datetime_start,
                    pytz.UTC.localize(
                        fields.Datetime.from_string(shift.start_date),
                        is_dst=False).astimezone(tz).replace(tzinfo=None)
                )
                dt_t = min(
                    datetime_end,
                    pytz.UTC.localize(
                        fields.Datetime.from_string(shift.end_date),
                        is_dst=False).astimezone(tz).replace(tzinfo=None)
                )
                yield self._interval_new(dt_f, dt_t, {'shifts': shift})

    @api.model
    def _interval_remove_leaves(self, interval, leave_intervals):
        # The shifts should not be affected by the holidays.
        # TODO: Shifts should be affected by the leaves?
        if 'shifts' in interval.data and interval.data['shifts']:
            return super()._interval_remove_leaves(interval, [])
        return super()._interval_remove_leaves(interval, leave_intervals)
