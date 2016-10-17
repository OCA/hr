# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.model
    def _check_date_helper(self, employee_id, date):
        status_id = self.holiday_status_id.id or self.env.context.get(
            'holiday_status_id',
            False)
        if employee_id and status_id:
            employee = self.env['hr.employee'].browse(employee_id)
            status = self.env['hr.holidays.status'].browse(status_id)
            if (not employee.work_scheduled_on_day(
                    fields.Date.from_string(date),
                    public_holiday=status.exclude_public_holidays,
                    schedule=status.exclude_rest_days)):
                return False
        return True

    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id(self):
        self._check_and_recompute_days()

    @api.onchange('employee_id')
    def _onchange_employee(self):
        super(HrHolidays, self)._onchange_employee()
        self._check_and_recompute_days()

    def _check_and_recompute_days(self):
        date_from = self.date_from
        date_to = self.date_to
        if (date_to and date_from) and (date_from <= date_to):
            if not self._check_date_helper(self.employee_id.id, date_from):
                raise ValidationError(_("You cannot schedule the start date "
                                        "on a public holiday or employee's "
                                        "rest day"))
            if not self._check_date_helper(self.employee_id.id, date_to):
                raise ValidationError(_("You cannot schedule the end date "
                                        "on a public holiday or employee's "
                                        "rest day"))
            self.number_of_days_temp = self._compute_number_of_days()

    @api.onchange('date_from')
    def _onchange_date_from(self):
        super(HrHolidays, self)._onchange_date_from()
        employee_id = self.employee_id.id
        if not self._check_date_helper(employee_id, self.date_from):
            raise ValidationError(_("You cannot schedule the start date on "
                                    "a public holiday or employee's rest day"))
        if (self.date_to and self.date_from) \
           and (self.date_from <= self.date_to):
            self.number_of_days_temp = self._compute_number_of_days()

    @api.onchange('date_to')
    def _onchange_date_to(self):
        super(HrHolidays, self)._onchange_date_to()
        employee_id = self.employee_id.id
        if not self._check_date_helper(employee_id, self.date_to):
            raise ValidationError(_("You cannot schedule the end date on "
                                    "a public holiday or employee's rest day"))
        if (self.date_to and self.date_from) \
           and (self.date_from <= self.date_to):
            self.number_of_days_temp = self._compute_number_of_days()

    def _compute_number_of_days(self):
        date_from = self.date_from
        date_to = self.date_to
        employee_id = self.employee_id.id
        if not date_from or not date_to:
            return 0
        days = self._get_number_of_days(date_from, date_to, None)
        if date_to == date_from:
            days = 1

        status_id = self.holiday_status_id.id or self.env.context.get(
            'holiday_status_id',
            False)
        if employee_id and date_from and date_to and status_id:
            employee = self.env['hr.employee'].browse(employee_id)
            status = self.env['hr.holidays.status'].browse(status_id)
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            date_dt = date_from
            while date_dt <= date_to:
                # if public holiday or rest day let us skip
                if not employee.work_scheduled_on_day(
                        date_dt,
                        status.exclude_public_holidays,
                        status.exclude_rest_days,
                ):
                    days -= 1
                date_dt += relativedelta(days=1)
        self.number_of_days = days
        return days
