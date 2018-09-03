# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import datetime
from dateutil import rrule


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _get_holidays_public_leaves(self, start_dt, end_dt, employe_id):
        """Get the public holidays for the current employee and given dates in
        the format expected by resource methods.

        :param: start_dt: Initial datetime.
        :param: end_dt: End datetime.
        :param: employee_id: Employee ID. It can be false.
        :return: List of tuples with (start_date, end_date) as elements.
        """
        leaves = []
        for day in rrule.rrule(rrule.YEARLY, dtstart=start_dt, until=end_dt):
            lines = self.env['hr.holidays.public'].get_holidays_list(
                day.year, employee_id=employe_id,
            )
            for line in lines:
                date = fields.Datetime.from_string(line.date)
                leaves.append(
                    (datetime.datetime.combine(date, datetime.time.min),
                     datetime.datetime.combine(date, datetime.time.max)),
                )
        return leaves

    @api.multi
    def _get_leave_intervals(self, resource_id=None,
                             start_datetime=None, end_datetime=None):
        res = super(ResourceCalendar, self)._get_leave_intervals(
            resource_id=resource_id,
            start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        if self.env.context.get('exclude_public_holidays'):
            res += self._get_holidays_public_leaves(
                start_datetime, end_datetime,
                self.env.context.get('employee_id', False),
            )
        return res
