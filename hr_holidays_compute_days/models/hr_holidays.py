# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import math


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

    @api.multi
    def onchange_employee(self, employee_id):
        res = super(HrHolidays, self).onchange_employee(employee_id)
        date_from = self.date_from or self.env.context.get('date_from')
        date_to = self.date_to or self.env.context.get('date_to')
        if (date_to and date_from) and (date_from <= date_to):
            if not self._check_date_helper(employee_id, date_from):
                raise ValidationError(_("You cannot schedule the start date "
                                        "on a public holiday or employee's "
                                        "rest day"))
            if not self._check_date_helper(employee_id, date_to):
                raise ValidationError(_("You cannot schedule the end date "
                                        "on a public holiday or employee's "
                                        "rest day"))
            duration = self._compute_number_of_days(employee_id,
                                                    date_to,
                                                    date_from)
            res['value']['number_of_days_temp'] = duration
        return res

    @api.multi
    def onchange_date_from(self, date_to, date_from):
        res = super(HrHolidays, self).onchange_date_from(date_to, date_from)
        employee_id = self.employee_id.id or self.env.context.get(
            'employee_id',
            False)
        if not self._check_date_helper(employee_id, date_from):
            raise ValidationError(_("You cannot schedule the start date on "
                                    "a public holiday or employee's rest day"))
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._compute_number_of_days(employee_id,
                                                    date_to,
                                                    date_from)
            res['value']['number_of_days_temp'] = diff_day
        return res

    @api.multi
    def onchange_date_to(self, date_to, date_from):
        res = super(HrHolidays, self).onchange_date_to(date_to, date_from)
        employee_id = self.employee_id.id or self.env.context.get(
            'employee_id',
            False)
        if not self._check_date_helper(employee_id, date_to):
            raise ValidationError(_("You cannot schedule the end date on "
                                    "a public holiday or employee's rest day"))
        if (date_to and date_from) and (date_from <= date_to):
            diff_day = self._compute_number_of_days(employee_id,
                                                    date_to,
                                                    date_from)
            res['value']['number_of_days_temp'] = diff_day
        return res

    def _compute_number_of_days(self, employee_id, date_to, date_from):
        if not date_from and not date_to:
            return 0
        days = self._get_number_of_days(date_from, date_to)
        if days or date_to == date_from:
            days = round(math.floor(days)) + 1
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
                        status.exclude_rest_days
                ):
                    days -= 1
                date_dt += relativedelta(days=1)
        return days
