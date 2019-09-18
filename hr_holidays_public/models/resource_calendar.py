# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# Copyright 2018 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models
from odoo.addons.resource.models.resource import Intervals

from pytz import timezone
from datetime import datetime, time
from dateutil import rrule


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _public_holidays_leave_intervals(self, start_dt, end_dt, employee_id,
                                         tz):
        """Get the public holidays for the current employee and given dates in
        the format expected by resource methods.

        :param: start_dt: Initial datetime.
        :param: end_dt: End datetime.
        :param: employee_id: Employee ID. It can be false.
        :return: List of tuples with (start_date, end_date) as elements.
        """
        HrHolidaysPublic = self.env['hr.holidays.public']

        leaves = []
        if start_dt.year != end_dt.year:
            # This fixes the case of leave request asked over 2 years.
            #
            # adding 1 year to end_dt for rrule to retrieve correct years for
            # public holidays to work
            # rrule.rrule(rrule.YEARLY, dtstart=2019-12-22, until=2020-01-05)
            # gives [2019]
            # rrule.rrule(rrule.YEARLY, dtstart=2019-12-22, until=2021-01-05)
            # gives [2019, 2020]
            end_dt = end_dt.replace(year=end_dt.year+1)

        for day in rrule.rrule(rrule.YEARLY, dtstart=start_dt, until=end_dt):
            lines = HrHolidaysPublic.get_holidays_list(
                day.year, employee_id=employee_id,
            )
            for line in lines:
                leaves.append(
                    (
                        datetime.combine(
                            line.date,
                            time.min
                        ).replace(tzinfo=tz),
                        datetime.combine(
                            line.date,
                            time.max
                        ).replace(tzinfo=tz),
                        line
                    ),
                )
        return Intervals(leaves)

    @api.multi
    def _leave_intervals(self, start_dt, end_dt, resource=None, domain=None):
        res = super()._leave_intervals(
            start_dt=start_dt,
            end_dt=end_dt,
            resource=resource,
            domain=domain,
        )
        if self.env.context.get('exclude_public_holidays'):
            tz = timezone((resource or self).tz)
            public_holidays = self._public_holidays_leave_intervals(
                start_dt,
                end_dt,
                self.env.context.get('employee_id', False),
                tz
            )
            res = res | public_holidays
        return res
