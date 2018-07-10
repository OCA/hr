# Copyright 2016 Odoo S. A.
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
import pytz
from dateutil import rrule

from odoo import api, models


def to_naive_user_tz(date_time, record):
    tz_name = record.env.context.get('tz') or record.env.user.tz
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(
        date_time.replace(tzinfo=None), is_dst=False,
    ).astimezone(tz).replace(tzinfo=None)


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def _get_leave_intervals(self, resource_id=None,
                             start_datetime=None, end_datetime=None):
        self.ensure_one()
        res = super(ResourceCalendar, self)._get_leave_intervals(
            resource_id=resource_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime)
        if self.env.context.get('employee') and \
                self.env.context.get('exclude_public_holidays'):
            employee = self.env.context.get('employee')[0]
            res += employee._get_holidays_public_leaves(
                start_datetime, end_datetime)
        return res

    def _iter_work_intervals(self, start_dt, end_dt,
                             resource_id, compute_leaves=True):
        """ This overwrite Odoo method.
        Lists the current resource's work intervals between the two provided
        datetimes (inclusive) expressed in UTC, for each worked day. """
        self.ensure_one()
        if not end_dt:
            end_dt = datetime.datetime.combine(start_dt.date(),
                                               datetime.time.max)

        start_dt = to_naive_user_tz(start_dt, self.env.user)
        end_dt = to_naive_user_tz(end_dt, self.env.user)
        real_weekdays = self._get_weekdays()
        if self.env.context.get('include_rest_days'):
            full_weekdays = range(7)
        else:
            full_weekdays = real_weekdays

        for day in rrule.rrule(rrule.DAILY,
                               dtstart=start_dt,
                               until=end_dt,
                               byweekday=full_weekdays):
            start_time = datetime.time.min
            if day.date() == start_dt.date():
                start_time = start_dt.time()
            end_time = datetime.time.max
            if day.date() == end_dt.date():
                end_time = end_dt.time()

            if day.weekday() in real_weekdays:
                intervals = self._get_day_work_intervals(
                    day.date(),
                    start_time=start_time,
                    end_time=end_time,
                    compute_leaves=compute_leaves,
                    resource_id=resource_id)
            else:  # Include full day for rest days - Will be handled later
                intervals = [(datetime.datetime.combine(day.date(),
                                                        datetime.time.min),
                              datetime.datetime.combine(day.date(),
                                                        datetime.time.max))]
            if intervals:
                yield intervals
