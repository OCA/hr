# -*- coding: utf-8 -*-
# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from dateutil import tz


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    from_half_day_am_pm = fields.Selection(
        selection=[('am', 'AM'),
                   ('pm', 'PM'), ],
        string='AM/PM',
        required=False,
        readonly=True,
        copy=False,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        default='am',
        help="If this the start date is half date please choose AM/PM.")

    to_half_day_am_pm = fields.Selection(
        selection=[('am', 'AM'),
                   ('pm', 'PM'), ],
        string='AM/PM',
        required=False,
        readonly=True,
        copy=False,
        default='am',
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
        help="If this the end date is half date please choose AM/PM.")

    from_half_day = fields.Boolean(
        readonly=True,
        copy=False,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    to_half_day = fields.Boolean(
        readonly=True,
        copy=False,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )

    from_full_day = fields.Boolean(
        default=True,
        readonly=True,
        copy=False,
        states={
            'draft': [('readonly', False)],
            'confirm': [('readonly', False)]
        },
    )
    to_full_day = fields.Boolean(
        default=True,
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
    # Support field for avoiding limitation on storing readonly fields
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

    @api.depends('date_from')
    def _compute_date_from_half(self):
        """Put day in employee's user timezone, or user timezone as fallback"""
        for record in self.filtered('date_from'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            dt = fields.Datetime.from_string(record.date_from).replace(
                tzinfo=tz.tzutc(),
            ).astimezone(tz.gettz(tz_name)).date()
            record.date_from_half = fields.Date.to_string(dt)

    @api.depends('date_to')
    def _compute_date_to_half(self):
        """Put day in employee's user timezone, or user timezone as fallback"""
        for record in self.filtered('date_to'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            dt = fields.Datetime.from_string(record.date_to).replace(
                tzinfo=tz.tzutc(),
            ).astimezone(tz.gettz(tz_name)).date()
            record.date_to_half = fields.Date.to_string(dt)

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
        for record in self.filtered(lambda r: not r.from_half_day):
            if record.date_from_full:
                tz_name = record.employee_id.user_id.tz or record.env.user.tz
                dt = fields.Datetime.from_string(record.date_from_full).replace(
                    hour=0, minute=0, second=0, microsecond=0,
                    tzinfo=tz.gettz(tz_name),
                ).astimezone(tz.tzutc())
                record.date_from = fields.Datetime.to_string(dt)
        for record in self.filtered('from_half_day'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            if not record.date_from_full:
                record.date_from_full = fields.Date.context_today(self)
            if record.from_half_day_am_pm == "am":
                dt = fields.Datetime.from_string(record.date_from_full).replace(
                    hour=8, minute=0, second=0, microsecond=0,
                    tzinfo=tz.gettz(tz_name),
                ).astimezone(tz.tzutc())
            else:
                dt = fields.Datetime.from_string(record.date_from_full).replace(
                    hour=12, minute=0, second=0, microsecond=0,
                    tzinfo=tz.gettz(tz_name),
                ).astimezone(tz.tzutc())
            record.date_from = fields.Datetime.to_string(dt)

    def _inverse_date_to_full(self):
        """Put end of the day in employee's user timezone, or user timezone
        as fallback.
        """
        for record in self.filtered(lambda r: not r.to_half_day):
            if record.date_to_full:
                tz_name = record.employee_id.user_id.tz or record.env.user.tz
                dt = fields.Datetime.from_string(record.date_to_full).replace(
                    hour=23, minute=59, second=59, microsecond=999999,
                    tzinfo=tz.gettz(tz_name),
                ).astimezone(tz.tzutc())
                record.date_to = fields.Datetime.to_string(dt)
        for record in self.filtered('to_half_day'):
            tz_name = record.employee_id.user_id.tz or record.env.user.tz
            if not record.date_to_full:
                record.date_to_full = fields.Date.context_today(self)
            if record.from_half_day_am_pm == "am":
                dt = fields.Datetime.from_string(record.date_to_full).replace(
                    hour=12, minute=0, second=0, microsecond=0,
                    tzinfo=tz.gettz(tz_name),
                ).astimezone(tz.tzutc())
            else:
                dt = fields.Datetime.from_string(record.date_to_full).replace(
                    hour=16, minute=0, second=0, microsecond=0,
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

    @api.onchange('date_from')
    def _onchange_date_from(self):
        """Recompute the adjusted value after the standard computation."""
        res = super(HrHolidays, self)._onchange_date_from()
        self._onchange_data_hr_holidays_compute_days()
        return res

    @api.onchange('date_to')
    def _onchange_date_to(self):
        """Recompute the adjusted value after the standard computation."""
        res = super(HrHolidays, self)._onchange_date_to()
        self._onchange_data_hr_holidays_compute_days()
        return res

    @api.onchange('from_half_day')
    def _onchange_from_half_day(self):
        """Or half or full, no other option for simplicity"""
        if not self.from_half_day:
            self.from_full_day = True
        self.from_full_day = False
        self._inverse_date_from_full()
        # if the leave if for one day just put half day in the to date as well
        # if not self.date_to:
        #    self.to_half_day = True
        self._onchange_data_hr_holidays_compute_days()

    @api.onchange('to_half_day')
    def _onchange_to_half_day(self):
        """Or half or full, no other option for simplicity"""
        if not self.to_half_day:
            self.to_full_day = True
        self.to_full_day = False
        self._inverse_date_to_full()
        # if the leave if for one day just put half day in the to date as well
        # if not self.date_from:
        #    self.from_half_day = True
        self._onchange_data_hr_holidays_compute_days()

    @api.onchange('employee_id', 'holiday_status_id')
    def _onchange_data_hr_holidays_compute_days(self):
        if self.date_to and self.date_from and self.date_from <= self.date_to:
            date_from = fields.Datetime.from_string(self.date_from)
            date_to = fields.Datetime.from_string(self.date_to)
            # The current user might not be linked to an employee
            # Odoo will handle the error when saving
            if not self.employee_id:
                return
            employee = self.employee_id
            if (self.holiday_status_id.exclude_public_holidays or
                not self.holiday_status_id):
                employee = employee.with_context(exclude_public_holidays=True)
            employee = employee.with_context(
                include_rest_days=not self.holiday_status_id.exclude_rest_days,
                compute_full_days=self.holiday_status_id.compute_full_days,
                current_leave=self
            )
            days = employee.get_work_days_count(
                from_datetime=date_from, to_datetime=date_to,
            )
            self.number_of_days_temp = days or 0
