# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models
from odoo.addons.resource.models.resource import to_naive_utc
from datetime import datetime, time


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _get_weekdays(self):
        """Include full week when we detect by context that we should include
        all days in leave computation.
        """
        if self.env.context.get('include_rest_days'):
            return range(7)
        return super()._get_weekdays()

    def _get_day_work_intervals(self, day_date, start_time=None, end_time=None,
                                compute_leaves=False, resource_id=None):
        """Return fake work intervals for full day when asking for rest days
        included through ``_get_weekdays``.
        """
        if self.env.context.get('include_rest_days'):
            real_weekdays = self.with_context(
                include_rest_days=False,
            )._get_weekdays()
            if day_date.weekday() not in real_weekdays:
                user = self.env.user
                return [self._interval_new(
                    to_naive_utc(datetime.combine(
                        day_date, time(hour=0, minute=0, second=0),
                    ), user),
                    to_naive_utc(datetime.combine(
                        day_date, time(hour=23, minute=59, second=59),
                    ), user),
                    {},
                )]
        return super()._get_day_work_intervals(
            day_date, start_time=start_time, end_time=end_time,
            compute_leaves=compute_leaves, resource_id=resource_id,
        )
