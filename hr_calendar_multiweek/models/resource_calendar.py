# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import timedelta
from odoo import api, fields, models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def _get_day_attendances(self, day_date, start_time, end_time):
        res = super()._get_day_attendances(day_date, start_time, end_time)
        return res.filtered(lambda r: r._check_week(day_date))


class ResourceCalendarAttendance(models.Model):
    _inherit = "resource.calendar.attendance"

    calendar_week_number = fields.Integer(
        default=1,
        help="Total number of weeks to use for the rule",
    )
    week_number = fields.Integer(
        default=1,
        help="Week when the rule must be applied",
    )

    _sql_constraints = [
        ('calendar_week_number_consistency',
         'CHECK(calendar_week_number >= 1)',
         'Calendar week number must be greater than 1'),
        ('week_number_consistency',
         'CHECK(week_number >= 1)',
         'Week number must be greater than 1'),
        ('week_number_consistency_max',
         'CHECK(calendar_week_number >= week_number)',
         'Week number must be less or equal than calendar week number'),
    ]

    @api.onchange('calendar_week_number')
    def _onchange_calendar_week_number(self):
        if self.week_number > self.calendar_week_number:
            self.week_number = self.calendar_week_number

    def _get_week_number(self, day_date):
        if self.date_from:
            date_from = fields.Date.from_string(self.date_from)
            weeks = 1 + divmod((day_date - (
                date_from + timedelta(days=-date_from.weekday()))).days, 7)[0]
        else:
            weeks = day_date.isocalendar()[1]
        number = divmod(weeks, self.calendar_week_number)[1]
        if number == 0:
            return self.calendar_week_number
        return number

    def _check_week(self, day_date):
        if not self.calendar_week_number or self.calendar_week_number == 1:
            return True
        return self.week_number == self._get_week_number(day_date)
