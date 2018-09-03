# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def get_day_work_hours_count(self, day_date, calendar=None):
        """Return 24 as work hours when detecting through context and weekday
        that the day passed is one of the rest days.
        """
        if self.env.context.get('include_rest_days') and calendar:
            real_weekdays = calendar.with_context(
                include_rest_days=False,
            )._get_weekdays()
            if day_date.weekday() not in real_weekdays:
                return 24
        return super().get_day_work_hours_count(day_date, calendar=calendar)
