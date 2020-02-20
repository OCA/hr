from odoo.addons.resource.models.resource_mixin import ResourceMixin, ROUNDING_FACTOR
from datetime import timedelta
from odoo.tools import float_utils
from pytz import utc
from collections import defaultdict


def post_load_hook():
    if not hasattr(ResourceMixin, 'get_work_days_data_original'):
        ResourceMixin.get_work_days_data_original = \
            ResourceMixin.get_work_days_data

    def __new_get_work_days_data(
            self, from_datetime, to_datetime, compute_leaves=True,
            calendar=None, domain=None
    ):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        # total hours per day: retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = calendar._attendance_intervals(
            from_full, to_full, resource
        )
        day_total = defaultdict(float)
        for start, stop, meta in intervals:
            day_total[start.date()] += (stop - start).total_seconds() / 3600

        # actual hours per day
        if compute_leaves:
            intervals = calendar._work_intervals(
                from_datetime, to_datetime, resource, domain
            )
        else:
            intervals = calendar._attendance_intervals(
                from_datetime, to_datetime, resource
            )
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += self._get_work_hours(start, stop, meta)

        # compute number of days as quarters
        days = sum(
            float_utils.round(
                ROUNDING_FACTOR * day_hours[day] / day_total[day]
            ) / ROUNDING_FACTOR
            for day in day_hours
        )
        return {
            'days': days,
            'hours': sum(day_hours.values()),
        }

    ResourceMixin.get_work_days_data = __new_get_work_days_data
