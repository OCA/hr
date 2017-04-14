# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, exceptions, fields, models, _


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
        date_dt = fields.Datetime.from_string(date)
        date_dt = fields.Datetime.context_timestamp(self, date_dt)
        return fields.Datetime.to_string(date_dt)

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
