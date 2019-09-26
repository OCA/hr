# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, date

from odoo import api, models, fields


class ResourceCalendar(models.Model):
    _inherit = "resource.calendar"

    @api.model
    def _get_work_limits(self, end_dt, start_dt):
        # Computes start_dt, end_dt (with default values if not set)
        # + off-interval work limits

        def set_work_limits_start(end_dt, start_dt):
            work_limits = []
            if start_dt is None and end_dt is not None:
                start_dt = end_dt.replace(
                    hour=0, minute=0, second=0, microsecond=0)
            elif start_dt is None:
                start_dt = datetime.now().replace(
                    hour=0, minute=0, second=0, microsecond=0)
            else:
                work_limits.append((start_dt.replace(
                    hour=0, minute=0, second=0, microsecond=0), start_dt))
            return start_dt, work_limits

        def set_work_limits_end(end_dt, start_dt, work_limits):
            if end_dt is None:
                end_dt = start_dt.replace(
                    hour=23, minute=59, second=59, microsecond=999999)
            else:
                work_limits.append((end_dt, end_dt.replace(
                    hour=23, minute=59, second=59, microsecond=999999)))
            return end_dt

        start_dt, work_limits = set_work_limits_start(end_dt, start_dt)
        end_dt = set_work_limits_end(end_dt, start_dt, work_limits)
        assert start_dt.date() == end_dt.date(), \
            'get_working_intervals_of_day is restricted to one day'
        return start_dt, work_limits

    @api.model
    def interval_remove_leaves(self, interval, leave_intervals):
        user = self.env.user
        new_leave_intervals = []
        if self.env.context.get('change_tz', False) and leave_intervals:
            this_year = date.today().year
            reference_date = fields.Datetime.context_timestamp(
                user,
                datetime(this_year, 1, 1, 12)
            )
            for l_interval in leave_intervals:
                new_interval = []
                for el in l_interval:
                    gmt_el = fields.Datetime.context_timestamp(user, el)
                    gmt_el_offset = gmt_el.tzinfo._utcoffset
                    ref_offset = reference_date.tzinfo._utcoffset
                    new_interval.append(el + gmt_el_offset - ref_offset)
                new_interval = tuple(new_interval)
                new_leave_intervals.append(new_interval)
        else:
            new_leave_intervals = leave_intervals

        return super(ResourceCalendar, self).interval_remove_leaves(
            interval,
            new_leave_intervals
        )
