# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# © 2016 MONK Software (http://www.wearemonk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.multi
    def _check_limits(self):
        if not self.holiday_status_id or not self.employee_id:
            return True
        for date in (self.date_from, self.date_to):
            should_work = self.employee_id.work_scheduled_on_day(
                fields.Date.from_string(date),
                public_holiday=self.holiday_status_id.exclude_public_holidays,
                schedule=self.holiday_status_id.exclude_rest_days)
            if not should_work:
                raise ValidationError(
                    _("This leave type doesn't allow leaves that start or end"
                      " on a non-working day for the employee."))

    def _check_and_recompute_days(self):
        date_from = self.date_from
        date_to = self.date_to
        if not date_from or not date_to or date_from > date_to:
            return
        self._check_limits()
        self.number_of_days_temp = self._get_number_of_days(
            date_from, date_to, self.employee_id)

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        self._check_and_recompute_days()

    @api.onchange('employee_id')
    def _onchange_employee(self):
        super(HrHolidays, self)._onchange_employee()
        self._check_and_recompute_days()

    @api.onchange('date_from')
    def _onchange_date_from(self):
        super(HrHolidays, self)._onchange_date_from()
        self._check_limits()

    @api.onchange('date_to')
    def _onchange_date_to(self):
        super(HrHolidays, self)._onchange_date_to()
        self._check_limits()

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if not self.holiday_status_id.allow_partial_days:
            date_from = fields.Datetime.from_string(date_from).replace(
                hour=0, minute=0, second=0, microsecond=0)
            date_to = fields.Datetime.from_string(date_to).replace(
                hour=23, minute=59, second=59, microsecond=0)
            date_from, date_to = [
                fields.Datetime.to_string(d) for d in (date_from, date_to)]
        return super(HrHolidays, self)._get_number_of_days(
            date_from, date_to, employee_id)
