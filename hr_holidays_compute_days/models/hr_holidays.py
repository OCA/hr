# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import time
from dateutil import tz


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    def _default_from_full_day(self):
        """Detect if we have select full day in calendar and return the
        full day option accordingly.
        """
        context = self.env.context
        if context.get('default_date_from'):
            dt = fields.Datetime.from_string(
                context['default_date_from']
            ).replace(tzinfo=tz.gettz(self.env.user.tz)).astimezone(tz.tzutc())
            return dt.hour == 5 and dt.minute == 0 and dt.second == 0
        return False

    def _default_to_full_day(self):
        """Detect if we have select full day in calendar and return the
        full day option accordingly.
        """
        context = self.env.context
        if context.get('default_date_to'):
            dt = fields.Datetime.from_string(
                context['default_date_to']
            ).replace(tzinfo=tz.gettz(self.env.user.tz)).astimezone(tz.tzutc())
            return dt.hour == 17 and dt.minute == 0 and dt.second == 0
        return False

    from_full_day = fields.Boolean(
        default=lambda self: self._default_from_full_day(),
        readonly=True,
        copy=False,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    to_full_day = fields.Boolean(
        default=lambda self: self._default_to_full_day(),
        readonly=True,
        copy=False,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    date_from_full = fields.Date(
        compute="_compute_date_from_full",
        inverse="_inverse_date_from_full",
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    date_to_full = fields.Date(
        compute="_compute_date_to_full",
        inverse="_inverse_date_to_full",
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    # Supporting field for avoiding limitation on storing readonly fields
    number_of_days_temp_related = fields.Float(
        related="number_of_days_temp", readonly=True,
    )

    @api.depends('date_from')
    def _compute_date_from_full(self):
        """Put day in employee's user timezone, or user timezone as fallback"""
        for record in self.filtered('date_from'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            dt = fields.Datetime.from_string(record.date_from).replace(
                tzinfo=tz.tzutc(),
            ).astimezone(tz.gettz(tz_name)).date()
            record.date_from_full = fields.Date.to_string(dt)

    @api.depends('date_to')
    def _compute_date_to_full(self):
        """Put day in employee's user timezone, or user timezone as fallback"""
        for record in self.filtered('date_to'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            dt = fields.Datetime.from_string(record.date_to).replace(
                tzinfo=tz.tzutc(),
            ).astimezone(tz.gettz(tz_name)).date()
            record.date_to_full = fields.Date.to_string(dt)

    def _inverse_date_from_full(self):
        """Put start of the day in employee's user timezone, or user timezone
        as fallback.
        """
        for record in self.filtered('from_full_day'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            dt = fields.Datetime.from_string(record.date_from_full).replace(
                hour=0, minute=0, second=0, microsecond=0,
                tzinfo=tz.gettz(tz_name),
            ).astimezone(tz.tzutc())
            record.date_from = fields.Datetime.to_string(dt)

    def _inverse_date_to_full(self):
        """Put end of the day in employee's user timezone, or user timezone
        as fallback.
        """
        for record in self.filtered('to_full_day'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            dt = fields.Datetime.from_string(record.date_to_full).replace(
                hour=23, minute=59, second=59, microsecond=999999,
                tzinfo=tz.gettz(tz_name),
            ).astimezone(tz.tzutc())
            record.date_to = fields.Datetime.to_string(dt)

    @api.onchange('date_from_full', 'from_full_day')
    def _onchange_date_from_full(self):
        """As inverse methods only works on save, we have to add an onchange"""
        self._inverse_date_from_full()

    @api.onchange('date_to_full', 'to_full_day')
    def _onchange_date_to_full(self):
        """As inverse methods only works on save, we have to add an onchange"""
        self._inverse_date_to_full()

    def _onchange_data_hr_holidays_compute_days(self):
        """Trigger the number of days computation also when you change the
        employee or the leave type.
        """
        self._onchange_date_to()

    def _get_number_of_days(self, date_from, date_to, employee_id):
        """Pass context variable for including rest days or change passed dates
        when computing full days.
        """
        obj = self.with_context(
            include_rest_days=not self.holiday_status_id.exclude_rest_days,
        )
        if self.holiday_status_id.compute_full_days:
            dt_from = fields.Datetime.from_string(date_from)
            date_from = fields.Datetime.to_string(
                dt_from.combine(
                    dt_from.date(), time(hour=0, minute=0, second=0),
                ),
            )
            dt_to = fields.Datetime.from_string(date_to)
            date_to = fields.Datetime.to_string(
                dt_to.combine(
                    dt_to.date(), time(hour=23, minute=59, second=59),
                ),
            )
        return super(HrHolidays, obj)._get_number_of_days(
            date_from, date_to, employee_id,
        )
