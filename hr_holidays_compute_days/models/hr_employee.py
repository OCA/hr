# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# © 2016 MONK Software (http://www.wearemonk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from openerp import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def work_scheduled_on_day(self, date_dt, public_holiday=True,
                              schedule=True, default_working_weekdays=None):
        """
        returns true or false depending on if employee was scheduled to work
        on a particular day. It does this by both checking if it is a public
        holiday and the resource calendar of the contract
        @param date_dt: date for which to check
        @param public_holiday: optional, whether to consider public holidays,
                               default=True
        @param schedule: optional, whether to consider the contract's resource
                         calendar or the default_working_weekdays. default=True
        @param default_working_weekdays: optional, days to consider as working
                                         days by default if the employee does
                                         not have a working time defined
        """
        self.ensure_one()
        if default_working_weekdays is None:
            # Monday - Friday by default
            default_working_weekdays = (0, 1, 2, 3, 4)

        if public_holiday and self.env['hr.holidays.public'].is_public_holiday(
                date_dt, employee_id=self.id):
            return False
        if schedule and self.calendar_id:
            hours = self.calendar_id.get_working_hours_of_date(
                datetime.combine(date_dt, time.min))
            return True if hours else False
        if schedule:
            return date_dt.weekday() in default_working_weekdays
        return True
