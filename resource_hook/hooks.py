from odoo.addons.resource.models.resource_mixin import ResourceMixin
from datetime import timedelta
from odoo.tools import float_utils


def post_load_hook():
    if not hasattr(ResourceMixin, 'get_work_days_data_original'):
        ResourceMixin.get_work_days_data_original = \
            ResourceMixin.get_work_days_data

    def __new_get_work_days_data(self, from_datetime, to_datetime,
                                 calendar=None):
        if not hasattr(self, '_get_work_hours'):
            return self.get_day_work_hours_count_original(
                from_datetime, to_datetime, calendar=calendar)
        days_count = 0.0
        total_work_time = timedelta()
        calendar = calendar or self.resource_calendar_id
        calendar = calendar.with_context(
            no_tz_convert=self.env.context.get('no_tz_convert', False))
        for day_intervals in calendar._iter_work_intervals(
                from_datetime, to_datetime, self.resource_id.id,
                compute_leaves=True):
            theoric_hours = self.get_day_work_hours_count(
                day_intervals[0][0].date(), calendar=calendar)
            # Here we introduce the hook method '_get_work_hours'.
            work_time = sum((self._get_work_hours(interval)
                             for interval in day_intervals), timedelta())
            total_work_time += work_time
            if theoric_hours:
                days_count += float_utils.round(
                    (work_time.total_seconds() / 3600 / theoric_hours) * 4) / 4
        return {
            'days': days_count,
            'hours': total_work_time.total_seconds() / 3600,
        }

    ResourceMixin.get_work_days_data = __new_get_work_days_data
