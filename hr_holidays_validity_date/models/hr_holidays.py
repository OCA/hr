# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_holidays_validity_date,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_holidays_validity_date is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_holidays_validity_date is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_holidays_validity_date.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, exceptions, _
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime
import pytz


class HrHolidaysStatus(models.Model):
    _inherit = "hr.holidays.status"

    date_start = fields.Datetime(string='Start Date')
    date_end = fields.Datetime(string="Expiry Date")
    use_validity_dates = fields.Boolean()

    _sql_constraints = [
        ('date_check',
         "CHECK ( (use_validity_dates=FALSE) OR (date_start <= date_end))",
         "The start date must be anterior to the end date."),
    ]


class HrHolidays(models.Model):
    _inherit = "hr.holidays"

    @api.model
    def _utc_to_tz(self, date):
        date_dt = datetime.strptime(date, DEFAULT_SERVER_DATETIME_FORMAT)
        tz_info = fields.Datetime.context_timestamp(self, date_dt).tzinfo
        date_dt = date_dt.replace(tzinfo=pytz.UTC).astimezone(tz_info)\
            .replace(tzinfo=None)
        return date_dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    @api.constrains('holiday_status_id', 'date_from', 'date_to')
    @api.one
    def _check_validity_date(self):
        if self.type == 'remove' and\
                self.holiday_status_id.use_validity_dates and\
                self.date_from and self.date_to:
            if self.date_from < self.holiday_status_id.date_start or\
                    self.date_to > self.holiday_status_id.date_end:
                tz_date_start = self._utc_to_tz(
                    self.holiday_status_id.date_start)
                tz_date_end = self._utc_to_tz(
                    self.holiday_status_id.date_end)
                raise exceptions.Warning(
                    _("""leaves on %s type must be taken between %s and
                    %s""") % (self.holiday_status_id.name,
                              tz_date_start,
                              tz_date_end))
