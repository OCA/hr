# -*- coding: utf-8 -*-
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
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
    def _check_validity_date(self):
        for rec in self:
            if (rec.type == 'remove' and
                    rec.holiday_status_id.use_validity_dates and
                    rec.date_from and rec.date_to):
                if (rec.date_from < rec.holiday_status_id.date_start or
                        rec.date_to > rec.holiday_status_id.date_end):
                    tz_date_start = rec._utc_to_tz(
                        rec.holiday_status_id.date_start)
                    tz_date_end = rec._utc_to_tz(
                        rec.holiday_status_id.date_end)
                    raise exceptions.Warning(
                        _("""leaves on %s type must be taken between %s and
                        %s""") % (rec.holiday_status_id.name,
                                  tz_date_start,
                                  tz_date_end))
