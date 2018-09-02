# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import pytz
from dateutil import tz
from odoo import api, fields, models


def to_naive_user_tz(date_time, record):
    tz_name = record.env.context.get('tz') or record.env.user.tz
    tz = pytz.timezone(tz_name) if tz_name else pytz.UTC
    return pytz.UTC.localize(
        date_time.replace(tzinfo=None), is_dst=False,
    ).astimezone(tz).replace(tzinfo=None)


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        super(HrHolidays, self)._onchange_employee_id()
        self._onchange_data_hr_holidays_compute_days()

    @api.onchange('date_from')
    def _onchange_date_from(self):
        if not self.holiday_status_id.compute_full_days:
            super(HrHolidays, self)._onchange_date_from()
        if self.holiday_status_id.compute_full_days and self.date_from:
            tz_name = self.employee_id.user_id.tz or self.env.user.tz
            start_dt = to_naive_user_tz(
                fields.Datetime.from_string(self.date_from), self)
            dt = start_dt.replace(
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=tz.gettz(tz_name),
            ).astimezone(tz.tzutc())
            self.date_from = fields.Datetime.to_string(dt)
            if self.date_to:
                end_dt = to_naive_user_tz(
                    fields.Datetime.from_string(self.date_to), self)
                dt = end_dt.replace(
                    hour=23, minute=59, second=59, microsecond=999999,
                    tzinfo=tz.gettz(tz_name),
                ).astimezone(tz.tzutc())
                self.date_to = fields.Datetime.to_string(dt)
        self._onchange_data_hr_holidays_compute_days()

    @api.onchange('date_to')
    def _onchange_date_to(self):
        super(HrHolidays, self)._onchange_date_to()
        if self.holiday_status_id.compute_full_days and self.date_to:
            tz_name = self.employee_id.user_id.tz or self.env.user.tz
            end_dt = to_naive_user_tz(
                fields.Datetime.from_string(self.date_to), self)
            dt = end_dt.replace(
                hour=23, minute=59, second=59, microsecond=999999,
                tzinfo=tz.gettz(tz_name),
            ).astimezone(tz.tzutc())
            self.date_to = fields.Datetime.to_string(dt)
        self._onchange_data_hr_holidays_compute_days()

    @api.onchange('employee_id', 'holiday_status_id')
    def _onchange_data_hr_holidays_compute_days(self):
        if self.date_to and self.date_from and self.date_from <= self.date_to:
            date_from = fields.Datetime.from_string(self.date_from)
            date_to = fields.Datetime.from_string(self.date_to)
            employee = self.employee_id
            employee = employee.with_context(employee=employee)
            if (self.holiday_status_id.exclude_public_holidays or
                    not self.holiday_status_id):
                employee = employee.with_context(exclude_public_holidays=True)
            employee = employee.with_context(
                include_rest_days=not self.holiday_status_id.exclude_rest_days,
                compute_full_days=self.holiday_status_id.compute_full_days,
            )
            datas = employee.get_work_days_data(from_datetime=date_from,
                                                to_datetime=date_to)
            if datas:
                self.number_of_days_temp = datas['days']
