from collections import defaultdict
from datetime import timedelta

from pytz import utc

from odoo.tools import float_utils
from odoo.tools.float_utils import float_round

from odoo.addons.resource.models.resource import (
    ROUNDING_FACTOR,
    ResourceCalendar,
    make_aware,
    partial,
)
from odoo.addons.resource.models.resource_mixin import ResourceMixin


def post_load_hook():  # noqa: C901

    # Functions to override
    resource_functions = [
        (ResourceCalendar, "_get_days_data"),
        (ResourceCalendar, "_get_resources_day_total"),
        (ResourceCalendar, "get_work_hours_count"),
        (ResourceCalendar, "plan_hours"),
        (ResourceCalendar, "_compute_hours_per_day"),
        (ResourceMixin, "list_work_time_per_day"),
        (ResourceMixin, "list_leaves"),
    ]

    for func in resource_functions:
        if not hasattr(func[0], func[1] + "_original"):
            old_function = getattr(func[0], func[1])
            setattr(func[0], func[1] + "_original", old_function)

    def __new__get_days_data(self, intervals, day_total):
        day_hours = defaultdict(float)
        for start, stop, meta in intervals:
            day_hours[start.date()] += self._get_work_hours_interval(start, stop, meta)

        # compute number of days as quarters
        days = sum(
            float_utils.round(ROUNDING_FACTOR * day_hours[day] / day_total[day])
            / ROUNDING_FACTOR
            for day in day_hours
        )
        return {
            "days": days,
            "hours": sum(day_hours.values()),
        }

    def __new__get_resources_day_total(
        self, from_datetime, to_datetime, resources=None
    ):
        self.ensure_one()
        resources = self.env["resource.resource"] if not resources else resources
        resources_list = list(resources) + [self.env["resource.resource"]]
        # total hours per day:  retrieve attendances with one extra day margin,
        # in order to compute the total hours on the first and last days
        from_full = from_datetime - timedelta(days=1)
        to_full = to_datetime + timedelta(days=1)
        intervals = self._attendance_intervals_batch(
            from_full, to_full, resources=resources
        )

        result = defaultdict(lambda: defaultdict(float))
        for resource in resources_list:
            day_total = result[resource.id]
            for start, stop, meta in intervals[resource.id]:
                day_total[start.date()] += self._get_work_hours_interval(
                    start, stop, meta
                )
        return result

    def __new_get_work_hours_count(
        self, start_dt, end_dt, compute_leaves=True, domain=None
    ):
        # Set timezone in UTC if no timezone is explicitly given
        if not start_dt.tzinfo:
            start_dt = start_dt.replace(tzinfo=utc)
        if not end_dt.tzinfo:
            end_dt = end_dt.replace(tzinfo=utc)

        if compute_leaves:
            intervals = self._work_intervals_batch(start_dt, end_dt, domain=domain)[
                False
            ]
        else:
            intervals = self._attendance_intervals_batch(start_dt, end_dt)[False]

        return sum(
            self._get_work_hours_interval(start, stop, meta)
            for start, stop, meta in intervals
        )

    def __new_plan_hours(
        self, hours, day_dt, compute_leaves=False, domain=None, resource=None
    ):
        day_dt, revert = make_aware(day_dt)

        # which method to use for retrieving intervals
        if compute_leaves:
            get_intervals = partial(
                self._work_intervals, domain=domain, resource=resource
            )
        else:
            get_intervals = self._attendance_intervals

        if hours >= 0:
            delta = timedelta(days=14)
            for n in range(100):
                dt = day_dt + delta * n
                for start, stop, meta in get_intervals(dt, dt + delta):
                    interval_hours = self._get_work_hours_interval(start, stop, meta)
                    if hours <= interval_hours:
                        return revert(start + timedelta(hours=hours))
                    hours -= interval_hours
            return False
        else:
            hours = abs(hours)
            delta = timedelta(days=14)
            for n in range(100):
                dt = day_dt - delta * n
                for start, stop, meta in reversed(get_intervals(dt - delta, dt)):
                    interval_hours = self._get_work_hours_interval(start, stop, meta)
                    if hours <= interval_hours:
                        return revert(stop - timedelta(hours=hours))
                    hours -= interval_hours
            return False

    def __new__compute_hours_per_day(self, attendances):
        if not attendances:
            return 0

        hour_count = 0.0
        for attendance in attendances:
            hour_count += self._get_work_hours_attendance(attendance)

        if self.two_weeks_calendar:
            number_of_days = len(
                set(
                    attendances.filtered(lambda cal: cal.week_type == "1").mapped(
                        "dayofweek"
                    )
                )
            )
            number_of_days += len(
                set(
                    attendances.filtered(lambda cal: cal.week_type == "0").mapped(
                        "dayofweek"
                    )
                )
            )
        else:
            number_of_days = len(set(attendances.mapped("dayofweek")))

        return float_round(hour_count / float(number_of_days), precision_digits=2)

    def __new_list_work_time_per_day(
        self, from_datetime, to_datetime, calendar=None, domain=None
    ):
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        intervals = calendar._work_intervals_batch(
            from_datetime, to_datetime, resource, domain
        )[resource.id]
        result = defaultdict(float)
        for start, stop, meta in intervals:
            result[start.date()] += self._get_work_hours_interval(start, stop, meta)
        return sorted(result.items())

    def __new_list_leaves(self, from_datetime, to_datetime, calendar=None, domain=None):
        resource = self.resource_id
        calendar = calendar or self.resource_calendar_id

        # naive datetimes are made explicit in UTC
        if not from_datetime.tzinfo:
            from_datetime = from_datetime.replace(tzinfo=utc)
        if not to_datetime.tzinfo:
            to_datetime = to_datetime.replace(tzinfo=utc)

        attendances = calendar._attendance_intervals_batch(
            from_datetime, to_datetime, resource
        )[resource.id]
        leaves = calendar._leave_intervals_batch(
            from_datetime, to_datetime, resource, domain
        )[resource.id]
        result = []
        for start, stop, leave in leaves & attendances:
            hours = self._get_work_hours_interval(start, stop, leave)
            result.append((start.date(), hours, leave))
        return result

    for func in resource_functions:
        setattr(func[0], func[1], locals()["__new_" + func[1]])
