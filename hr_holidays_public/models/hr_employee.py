# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime
from datetime import timedelta
from dateutil import rrule
from odoo import fields, models
from odoo.tools import float_utils


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_holidays_public_leaves(self, start_dt, end_dt):
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
                    datetime.datetime.combine(date, datetime.time.min),
                    datetime.datetime.combine(date, datetime.time.max)))
        return leaves

    def get_work_days_data(self, from_datetime, to_datetime, calendar=None):
        res = super(HrEmployee, self).get_work_days_data(
            from_datetime=from_datetime, to_datetime=to_datetime,
            calendar=calendar)
        self.ensure_one()
        days_count = 0.0
        total_work_time = timedelta()
        calendar = calendar or self.resource_calendar_id
        for day_intervals in calendar._iter_work_intervals(
                from_datetime, to_datetime, self.resource_id.id,
                compute_leaves=True):
            theoric_hours = self.get_day_work_hours_count(
                day_intervals[0][0].date(), calendar=calendar)
            work_time = sum(
                (interval[1] - interval[0] for interval in day_intervals),
                timedelta())
            total_work_time += work_time
            if theoric_hours:
                days_count += work_time.total_seconds() / 3600 / theoric_hours
            else:
                days_count += 1.0
        res['days'] = float_utils.float_round(days_count, precision_digits=3)
        res['hours'] = float_utils.float_round(
                total_work_time.total_seconds() / 3600, precision_digits=3)
        return res
