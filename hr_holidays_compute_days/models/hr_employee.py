# -*- coding: utf-8 -*-
# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta
from dateutil import rrule
from odoo import fields, models
from odoo.tools.float_utils import float_is_zero


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_public_holidays_leaves(self, start_dt, end_dt):
        """Get the public holidays for the current employee and given dates in
        the format expected by resource methods.

        :param: start_dt: Initial datetime.
        :param: end_dt: End datetime.
        :return: List of tuples with (start_date, end_date) as elements.
        """
        self.ensure_one()
        leaves = []
        for day in rrule.rrule(rrule.YEARLY, dtstart=start_dt, until=end_dt):
            lines = self.env['hr.holidays.public'].get_holidays_list(
                day.year, employee_id=self.id,
            )
            for line in lines:
                date = fields.Datetime.from_string(line.date)
                leaves.append((
                    date.replace(hour=0, minute=0, second=0, microsecond=0),
                    date.replace(
                        hour=23, minute=59, second=59, microsecond=999999,
                    ),
                ))
        return leaves

    def get_work_days_count(self, from_datetime, to_datetime, calendar=None):
        """Get the number or fraction of days that corresponds to this
        employee according its working time, leaves and public holidays.
        """
        self.ensure_one()
        days_count = 0.0
        calendar = calendar or self.calendar_id
        if not calendar:
            return days_count
        leaves = calendar.get_leave_intervals(resource_id=self.resource_id.id)
        # Add public holidays to leaves
        if self.env.context.get('exclude_public_holidays'):
            leaves += self._get_public_holidays_leaves(
                from_datetime, to_datetime,
            )
        for day_intervals in calendar._iter_work_intervals(
                from_datetime, to_datetime, leaves=leaves):
            if self.env.context.get('compute_full_days'):
                days_count += 1
                continue
            theoric_hours = calendar.get_working_hours_of_date(
                start_dt=day_intervals[0][0].replace(
                    hour=0, minute=0, second=0, microsecond=0,
                ),
                leaves=leaves,
                compute_leaves=False,
                resource_id=self.resource_id,
            )
            if float_is_zero(theoric_hours, 2):
                # This is because a rest day doesn't contain theoric hours,
                # but if it's included in the loop, it's because we want to
                # compute them, and they can only fully count.
                days_count += 1
                continue
            work_time = sum(
                (interval[1] - interval[0] for interval in day_intervals),
                timedelta(),
            )
            days_count += work_time.total_seconds() / 3600 / theoric_hours
        return round(days_count, 2)
