# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import babel.dates
from datetime import datetime, time
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_utils
from odoo.addons.resource.models.resource_mixin import ROUNDING_FACTOR


class HrLeaveWizard(models.TransientModel):
    _name = 'hr.leave.wizard'
    _description = 'HR Leave Wizard'

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        required=True,
        default=lambda self: self._default_employee_id(),
    )
    name = fields.Char(
        string='Description',
    )
    leave_type_id = fields.Many2one(
        string='Leave Type',
        comodel_name='hr.leave.type',
        required=True,
        domain=[('valid', '=', True)],
    )
    leave_type_request_unit = fields.Selection(
        related='leave_type_id.request_unit',
    )
    date_from = fields.Date(
        string='Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_to = fields.Date(
        string='End Date',
        required=True,
        default=fields.Date.context_today,
    )
    day_ids = fields.One2many(
        string='Days',
        comodel_name='hr.leave.wizard.day',
        inverse_name='wizard_id',
    )
    interval_ids = fields.One2many(
        string='Intervals',
        comodel_name='hr.leave.wizard.day.interval',
        inverse_name='wizard_id',
    )

    def _default_employee_id(self):
        return self.env.context.get('default_employee_id') or \
            self.env['hr.employee'].search([
                ('user_id', '=', self.env.uid)
            ], limit=1)

    @api.multi
    @api.onchange('date_from', 'date_to')
    def _onchange_date_range(self):
        self.ensure_one()
        if self.date_to < self.date_from:
            self.date_to = self.date_from
        self._generate_days()

    @api.multi
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self._generate_days()

    @api.multi
    @api.onchange('leave_type_id')
    def _onchange_leave_type_id(self):
        self._generate_days()

    @api.multi
    def _generate_days(self):
        HrLeaveWizardDay = self.env['hr.leave.wizard.day']
        for wizard in self:
            day_ids = HrLeaveWizardDay
            date = wizard.date_from
            while date <= wizard.date_to:
                day_ids |= HrLeaveWizardDay.new(
                    HrLeaveWizardDay._prepare_values(
                        wizard,
                        date,
                    )
                )
                date += relativedelta(days=1)
            wizard.day_ids = day_ids
            wizard.day_ids._generate_intervals()
            wizard.interval_ids = wizard.day_ids.mapped('interval_ids')

    @api.model
    def default_get(self, fields_list):
        defaults = super().default_get(fields_list)

        leave_type_id = self.env['hr.leave.type'].with_context(
            employee_id=defaults.get('employee_id'),
            default_date_from=defaults.get(
                'date_from',
                fields.Datetime.now()
            ),
        ).search(
            [('valid', '=', True)],
            limit=1,
        )

        if leave_type_id:
            defaults['leave_type_id'] = leave_type_id.id

        return defaults

    @api.multi
    def generate_leaves(self):
        leave_requests = []
        for wizard in self:
            if wizard.leave_type_request_unit == 'day':
                wizard.day_ids._recompute_request_amount_downward()
            elif wizard.leave_type_request_unit == 'hour':
                wizard.day_ids._recompute_request_amount_upward()
            else:  # pragma: no cover
                raise UserError(_(
                    'Unknown leave type request unit: %s'
                ) % (
                    wizard.leave_type_request_unit,
                ))

            draft_leave_requests = []
            index = 0
            while index < len(wizard.interval_ids):
                interval = wizard.interval_ids[index]
                if interval.requested_hours > 0.0:
                    if interval.requested_hours >= interval.available_hours \
                            and interval.available_hours > 0.0:
                        while index + len(interval) < len(wizard.interval_ids):
                            other_interval = wizard.interval_ids[
                                index + len(interval)
                            ]
                            if other_interval.requested_hours <= 0.0:
                                break
                            interval |= other_interval
                    draft_leave_requests.append(
                        interval._prepare_hr_leave_values()
                        if len(interval) == 1
                        else interval._prepare_merged_hr_leave_values()
                    )
                index += len(interval)

            for index, draft_leave_request in enumerate(draft_leave_requests):
                draft_leave_request.update({
                    'name': '%(name)s (%(index)s/%(count)s)' % {
                        'name': wizard.name or '',
                        'index': index + 1,
                        'count': len(draft_leave_requests),
                    },
                })
                leave_requests.append(draft_leave_request)

        return self.env['hr.leave'].create(leave_requests)

    @api.multi
    def action_submit(self):  # pragma: no cover
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.leave',
            'view_mode': 'tree',
            'views': [[False, 'tree']],
            'context': {
                'search_default_id': self.generate_leaves().ids,
            },
        }


class HrLeaveWizardDay(models.TransientModel):
    _name = 'hr.leave.wizard.day'
    _description = 'HR Leave Wizard Day'
    _order = 'date asc, id'

    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='hr.leave.wizard',
        required=True,
        ondelete='cascade',
    )
    leave_type_request_unit = fields.Selection(
        related='wizard_id.leave_type_id.request_unit',
    )
    date = fields.Date(
        string='Date',
        required=True,
        index=True,
    )
    name = fields.Char(
        compute='_compute_name',
    )
    interval_ids = fields.One2many(
        string='Intervals',
        comodel_name='hr.leave.wizard.day.interval',
        inverse_name='day_id',
    )
    request_amount = fields.Float(
        string='Request (%)',
    )
    available_hours = fields.Float(
        string='Available (hours)',
        compute='_compute_available_hours',
    )
    available_days = fields.Float(
        string='Available (days)',
        compute='_compute_available_days',
    )
    requested_days = fields.Float(
        string='Requested (days)',
        compute='_compute_requested',
        inverse='_inverse_requested_days',
    )
    requested_hours = fields.Float(
        string='Requested (hours)',
        compute='_compute_requested',
        inverse='_inverse_requested_hours',
    )

    _sql_constraints = [
        ('day_uniq', 'unique(wizard_id, date)', 'Date has to be unique!'),
    ]

    @api.multi
    @api.depends('date')
    def _compute_name(self):
        locale = self.env.context.get('lang') or 'en_US'

        for day in self:
            day.name = babel.dates.format_skeleton(
                skeleton='MMMEd',
                datetime=datetime.combine(day.date, time.min),
                locale=locale,
            )

    @api.multi
    def _generate_intervals(self):
        HrLeaveWizardDayInterval = self.env['hr.leave.wizard.day.interval']
        for day in self:
            employee = day.wizard_id.employee_id
            if not employee.resource_id:  # pragma: no cover
                day.interval_ids = [(5, 0, 0)]
                continue

            day_start = datetime.combine(day.date, time.min)
            day_end = datetime.combine(day.date, time.max)
            day_start = day_start.replace(tzinfo=utc)
            day_end = day_end.replace(tzinfo=utc)

            calendar = employee.resource_calendar_id
            attendance_intervals = calendar._attendance_intervals(
                day_start,
                day_end,
                employee.resource_id,
            )
            unpaid_intervals = calendar._leave_intervals(
                day_start,
                day_end,
                employee.resource_id,
            )
            global_intervals = calendar._leave_intervals(
                day_start,
                day_end,
                None,
            )
            intervals = (
                attendance_intervals - (unpaid_intervals - global_intervals)
            )

            interval_ids = [(5, 0, 0)]
            for start, stop, meta in intervals:
                values = HrLeaveWizardDayInterval._prepare_values(
                    start.astimezone(utc).replace(tzinfo=None),
                    stop.astimezone(utc).replace(tzinfo=None),
                )
                interval_ids += [(0, 0, values)]
            day.interval_ids = interval_ids

    @api.multi
    def _recompute_request_amount_upward(self):
        for day in self:
            day.request_amount = sum(
                day.interval_ids.mapped('request_amount')
            ) / len(day.interval_ids) if day.interval_ids else 0.0

    @api.multi
    def _recompute_request_amount_downward(self):
        for day in self:
            if day.requested_hours >= day.available_hours \
                    and day.available_hours > 0.0:
                for interval in day.interval_ids:
                    interval.request_amount = 1.0
            elif day.requested_hours <= 0.0 or day.available_hours <= 0.0:
                for interval in day.interval_ids:
                    interval.request_amount = 0.0
            else:
                requested_hours = day.requested_hours
                for interval in day.interval_ids:
                    if interval.available_hours > 0:
                        interval.request_amount = min(
                            requested_hours,
                            interval.available_hours
                        ) / interval.available_hours
                    else:
                        interval.request_amount = 0.0
                    requested_hours -= interval.requested_hours

    @api.multi
    @api.depends('interval_ids.available_days')
    def _compute_available_days(self):
        for day in self:
            day.available_days = sum(
                day.interval_ids.mapped('available_days')
            )

    @api.multi
    @api.depends('interval_ids.available_hours')
    def _compute_available_hours(self):
        for day in self:
            day.available_hours = sum(
                day.interval_ids.mapped('available_hours')
            )

    @api.multi
    @api.depends('request_amount', 'available_hours', 'available_days')
    def _compute_requested(self):
        for day in self:
            day.requested_hours = day.available_hours * day.request_amount
            day.requested_days = day.available_days * day.request_amount

    @api.multi
    def _inverse_requested_days(self):
        for day in self:
            amount = (float_utils.round(
                ROUNDING_FACTOR * day.requested_days / day.available_days
            ) / ROUNDING_FACTOR) if day.available_days else 0.0
            day.request_amount = max(min(amount, 1.0), 0.0)

    @api.multi
    def _inverse_requested_hours(self):
        for day in self:
            amount = (float_utils.round(
                ROUNDING_FACTOR * day.requested_hours / day.available_hours
            ) / ROUNDING_FACTOR) if day.available_hours else 0.0
            day.request_amount = max(min(amount, 1.0), 0.0)

    @api.multi
    @api.onchange('requested_days')
    def _onchange_requested_days(self):
        self._inverse_requested_days()

    @api.multi
    @api.onchange('requested_hours')
    def _onchange_requested_hours(self):
        self._inverse_requested_hours()

    @api.model
    def _prepare_values(self, wizard, date):
        return {
            'date': date,
            'request_amount': 1.0,
        }


class HrLeaveWizardDayInterval(models.TransientModel):
    _name = 'hr.leave.wizard.day.interval'
    _description = 'HR Leave Wizard Day Interval'
    _order = 'since asc, id'

    day_id = fields.Many2one(
        string='Day',
        comodel_name='hr.leave.wizard.day',
        required=True,
        ondelete='cascade',
    )
    day_name = fields.Char(
        string='Day Name',
        related='day_id.name',
    )
    wizard_id = fields.Many2one(
        string='Wizard',
        comodel_name='hr.leave.wizard',
        related='day_id.wizard_id',
    )
    date = fields.Date(
        related='day_id.date',
    )
    since = fields.Datetime(
        string='Since',
        required=True,
    )
    until = fields.Datetime(
        string='Until',
        required=True,
    )
    request_amount = fields.Float(
        string='Request (%)',
    )
    leave_type_request_unit = fields.Selection(
        related='day_id.leave_type_request_unit',
    )
    name = fields.Char(
        compute='_compute_name',
    )
    available_hours = fields.Float(
        string='Available (hours)',
        compute='_compute_available_hours',
    )
    available_days = fields.Float(
        string='Available (days)',
        compute='_compute_available_days',
    )
    requested_days = fields.Float(
        string='Requested (days)',
        compute='_compute_requested',
        inverse='_inverse_requested_days',
    )
    requested_hours = fields.Float(
        string='Requested (hours)',
        compute='_compute_requested',
        inverse='_inverse_requested_hours',
    )

    @api.multi
    @api.depends('since', 'until')
    def _compute_name(self):
        user_tz = timezone(self.env.context.get('tz') or 'UTC')
        locale = self.env.context.get('lang') or 'en_US'

        for interval in self:
            since = interval.since.replace(tzinfo=utc)
            since = since.astimezone(user_tz)
            until = interval.until.replace(tzinfo=utc)
            until = until.astimezone(user_tz)
            interval.name = _('%(since)s - %(until)s') % {
                'since': babel.dates.format_skeleton(
                    skeleton='HHmm',
                    datetime=since,
                    locale=locale,
                ),
                'until': babel.dates.format_skeleton(
                    skeleton='HHmm',
                    datetime=until,
                    locale=locale,
                ),
            }

    @api.multi
    @api.depends('since', 'until')
    def _compute_available_hours(self):
        for interval in self:
            interval.available_hours = (
                interval.until - interval.since
            ).total_seconds() / 3600

    @api.multi
    @api.depends('available_hours', 'day_id.available_hours')
    def _compute_available_days(self):
        for interval in self:
            available_hours = interval.day_id.available_hours
            hours = interval.available_hours
            interval.available_days = (float_utils.round(
                ROUNDING_FACTOR * hours / available_hours
            ) / ROUNDING_FACTOR) if available_hours else 0.0

    @api.multi
    @api.depends(
        'available_hours',
        'available_days',
        'request_amount',
    )
    def _compute_requested(self):
        for interval in self:
            interval.requested_hours = (
                interval.available_hours * interval.request_amount
            )
            interval.requested_days = (
                interval.available_days * interval.request_amount
            )

    @api.multi
    def _inverse_requested_days(self):
        for interval in self:
            amount = (float_utils.round(
                ROUNDING_FACTOR * (
                    interval.requested_days
                ) / interval.available_days
            ) / ROUNDING_FACTOR) if interval.available_days else 0.0
            interval.request_amount = max(min(amount, 1.0), 0.0)

    @api.multi
    def _inverse_requested_hours(self):
        for interval in self:
            amount = (float_utils.round(
                ROUNDING_FACTOR * (
                    interval.requested_hours / interval.available_hours
                )
            ) / ROUNDING_FACTOR) if interval.available_hours else 0.0
            interval.request_amount = max(min(amount, 1.0), 0.0)

    @api.multi
    @api.onchange('requested_days')
    def _onchange_requested_days(self):
        self._inverse_requested_days()

    @api.multi
    @api.onchange('requested_hours')
    def _onchange_requested_hours(self):
        self._inverse_requested_hours()

    @api.multi
    def _prepare_hr_leave_values(self):
        self.ensure_one()
        return {
            'employee_id': self.wizard_id.employee_id.id,
            'holiday_status_id': self.wizard_id.leave_type_id.id,
            'number_of_days': self.requested_days,
            'date_from': self.since,
            'date_to': min(
                self.until,
                self.since + relativedelta(
                    hours=self.requested_hours
                )
            ),
        }

    @api.multi
    def _prepare_merged_hr_leave_values(self):
        return {
            'employee_id': self[0].wizard_id.employee_id.id,
            'holiday_status_id': self[0].wizard_id.leave_type_id.id,
            'number_of_days': sum(self.mapped('requested_days')),
            'date_from': self[0].since,
            'date_to': self[-1].until,
        }

    @api.model
    def _prepare_values(self, since, until):
        return {
            'since': since,
            'until': until,
            'request_amount': 1.0,
        }
