# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import math


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _check_date_helper(self, date):
        if (not self.employee_id.work_scheduled_on_day(
                fields.Date.from_string(date),
                public_holiday=self.holiday_status_id.exclude_public_holidays,
                schedule=self.holiday_status_id.exclude_rest_days)):
            return False
        return True

    @api.constrains('date_from')
    @api.model
    def _check_date_from(self):
        if not self._check_date_helper(self.date_from):
            raise ValidationError('You cannot schedule the start date on '
                                  'a public holiday or employee\'s rest day')
        return True

    @api.constrains('date_to')
    @api.model
    def _check_date_to(self):
        if not self._check_date_helper(self.date_to):
            raise ValidationError('You cannot schedule the end date on '
                                  'a public holiday or employee\'s rest day')
        return True

    def _compute_number_of_days(self):
        date_from = self.date_from
        date_to = self.date_to
        days = self._get_number_of_days(date_from, date_to)
        if days:
            days = round(math.floor(days))+1

        if (self.type == 'remove' and self.holiday_type == 'employee'
                and self.employee_id and days):
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            date_dt = date_from
            while date_dt <= date_to:
                # if public holiday or rest day let us skip
                if not self.employee_id.work_scheduled_on_day(
                    date_dt,
                    self.holiday_status_id.exclude_public_holidays,
                    self.holiday_status_id.exclude_rest_days
                ):
                    days -= 1
                date_dt += relativedelta(days=1)
        return days

    @api.onchange(
        'employee_id', 'number_of_days_temp', 'date_from', 'holiday_type',
        'holiday_status_id', 'date_to', 'type')
    @api.multi
    def on_change_number_of_days(self):
        self.ensure_one()
        if(
            self.type == 'remove'
            and self.date_from
            and self.date_to
            and (self.date_from <= self.date_to)
        ):
            # Compute and update the number of days
            days = self._compute_number_of_days()
            self.number_of_days_temp = days
