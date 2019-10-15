# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# Author: Quentin Gigon <gigon.quentin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import datetime
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class HrEmployeePeriod(models.Model):
    _name = "hr.employee.period"

    _order = "start_date"

    current = fields.Boolean()
    attendance_day_ids = fields

    start_date = fields.Date(string='First date of period')
    end_date = fields.Date(string='Last date of period')
    end_date_display = fields.Date(string="Last date of period",
                                   compute="_compute_display_of_end_date")
    balance = fields.Float(readonly=True)
    final_balance = fields.Float(compute='_compute_final_balance', readonly=True)
    previous_period = fields.Many2one('hr.employee.period')
    previous_balance = fields.Float('previous balance')
    lost = fields.Float(string='Hours lost', readonly=True)
    employee_id = fields.Many2one("hr.employee", string='Employee', readonly=True)
    continuous_cap = fields.Boolean(string='Continuous cap for this period')

    @api.depends('end_date')
    def _compute_display_of_end_date(self):
        for period in self:
            if period.end_date:
                period.end_date_display = datetime.datetime.strptime(period.end_date, '%Y-%m-%d') \
                                          - datetime.timedelta(days=1)

    @api.depends('previous_period', 'balance')
    def _compute_final_balance(self):
        for period in self.filtered('previous_period'):
            period.final_balance = period.previous_period.final_balance + period.balance

    # Called when past periods must be updated (balance), often after an update to an attendance_day
    def update_past_periods(self, balance):
        """
        This function recompute balance and lost hours for a period.
        Used when an attendance_day was modified and when the continuous_cap of a period is modified
        :param start_date: start date for the update
        :param end_date: date of end of first period
        :param balance: balance before start_date
        :return:
        """
        employee = self.employee_id

        for current_period in self:
            start_date = current_period.start_date
            end_date = current_period.end_date

            extra, lost = employee.past_balance_computation(
                start_date=start_date,
                end_date=end_date,
                existing_balance=balance)

            current_period.write({
                'final_balance': extra,
                'balance': extra - balance,
                'lost': lost,
                'previous_balance': balance
            })

            employee_next_periods = self.env['hr.employee.period'].search([
                ('employee_id', '=', employee.id),
                ('end_date', '>', end_date)
            ], order='end_date asc')

            previous_balance = extra

            # Modify each following history entry
            for period in employee_next_periods:
                period.balance, period.lost = employee.past_balance_computation(
                    start_date=period.start_date,
                    end_date=period.end_date,
                    existing_balance=previous_balance
                )
                period.write({
                    'previous_balance': previous_balance,
                    'balance': period.balance - previous_balance,
                    'final_balance': period.balance,
                    'lost': period.lost
                })
                previous_balance = period.balance

    @api.multi
    def write(self, vals):
        res = super(HrEmployeePeriod, self).write(vals)
        for period in self:
            if 'continuous_cap' in vals or 'end_date' in vals or 'start_date' in vals:
                previous_period = self.env['hr.employee.period'].search([
                    ('employee_id', '=', period.employee_id.id),
                    ('end_date', '<=', period.start_date)
                ], order='end_date desc', limit=1)
                config = self.env['base.config.settings'].create({})
                config.set_beginning_date()
                start_date = None
                end_date = period.end_date
                balance = None

                if previous_period:
                    start_date = datetime.datetime.strptime(previous_period.end_date, '%Y-%m-%d')
                    balance = previous_period.balance
                    if 'start_date' in vals:
                        start_date = vals['start_date']
                    elif 'end_date' in vals:
                        end_date = vals['end_date']
                else:
                    start_date = config.get_beginning_date_for_balance_computation()
                    balance = period.employee_id.initial_balance

                period.update_past_periods(balance)
        return res

    @api.multi
    def create(self, vals):
        res = super(HrEmployeePeriod, self).create(vals)

        config = self.env['base.config.settings'].create({})
        start_date = vals['start_date']
        end_date = vals['end_date']

        origin = None
        if 'origin' in vals:
            origin = vals['origin']

        if end_date and start_date and not origin == "override":

            employee_periods = self.env['hr.employee.period'].search([
                ('employee_id', '=', vals['employee_id'])
            ])
            # last period before start_date
            previous_period = self.env['hr.employee.period'].search([
                ('employee_id', '=', vals['employee_id']),
                ('end_date', '<=', start_date)
            ], order='end_date desc', limit=1)
            # period that begins before and finish after start_date
            previous_overlapping_period = self.env['hr.employee.period'].search([
                ('employee_id', '=', vals['employee_id']),
                ('end_date', '>', start_date),
                ('end_date', '<', end_date),
                ('start_date', '<', start_date)
            ], order='end_date desc', limit=1)
            # period that begins before and finish after end_date
            next_overlapping_period = self.env['hr.employee.period'].search([
                ('employee_id', '=', vals['employee_id']),
                ('start_date', '>', start_date),
                ('start_date', '<', end_date),
                ('end_date', '>', end_date)
            ], order='start_date asc', limit=1)
            # period that begins before start_date and finish after end_date
            surrounding_period = self.env['hr.employee.period'].search([
                ('employee_id', '=', vals['employee_id']),
                ('start_date', '<', start_date),
                ('end_date', '>', end_date)
            ])

            employee = self.env['hr.employee'].search([
                    ('id', '=', vals['employee_id'])
                ])

            if isinstance(start_date, basestring):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

            if isinstance(end_date, basestring):
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

            # We want to create a period inside another one
            if surrounding_period:
                surround_start = surrounding_period.start_date
                surround_end = surrounding_period.end_date
                surround_continuous_cap = surrounding_period.continuous_cap
                employee_id = surrounding_period.employee_id
                surrounding_period.unlink()

                balance_previous = None
                if previous_period:
                    balance_previous = previous_period.balance
                else:
                    balance_previous = employee.initial_balance

                # Creates a period from the beginning of the surrounding period
                # to the beginning of the new period
                period1 = self.create_period(start_date=surround_start,
                                           end_date=start_date,
                                           employee_id=employee_id.id,
                                           balance=0,
                                           previous_balance=balance_previous,
                                           continuous_cap=surround_continuous_cap,
                                           origin="override")

                # Creates a period from the end of the new period
                # to the end of the surrounding period
                self.create_period(start_date=end_date,
                                   end_date=surround_end,
                                   employee_id=employee_id.id,
                                   balance=0,
                                   previous_balance=0,
                                   continuous_cap=surround_continuous_cap,
                                   origin="override")

                period1.update_past_periods(balance_previous)

            else:
                if previous_period:
                    previous_end_date = datetime.datetime.strptime(previous_period.end_date, '%Y-%m-%d')
                    # Periods not overlapping and with the space for a new one
                    if not previous_overlapping_period and (start_date - previous_end_date).days > 1:
                        # Creates period between previous_period.end_date and start_date of new one
                        period = self.create_period(start_date=previous_end_date,
                                           end_date=start_date,
                                           employee_id=previous_period.employee_id.id,
                                           balance=0,
                                           previous_balance=previous_period.balance,
                                           continuous_cap=self.employee_id.extra_hours_continuous_cap,
                                           origin="override")

                        period.update_past_periods(previous_period.balance)

                if previous_overlapping_period:
                    # Modify first previous overlapping period
                    previous_overlapping_period.write({
                        'end_date': start_date
                    })

                # A following period overlap with the new one
                if next_overlapping_period:
                    # Modify next overlapping period
                    next_overlapping_period.write({
                        'start_date': end_date
                    })
                # Only one period added, no funny stuff to do
                else:
                    employee_history_first_entry = self.env['hr.employee.period'].search([
                        ('employee_id', '=', employee.id),
                    ], order='start_date asc', limit=1)

                    employee_history_first_entry.update_past_periods(employee_history_first_entry.previous_balance)

        return res

    def create_period(self, start_date, end_date, employee_id, balance, previous_balance, continuous_cap, origin):
        return self.env['hr.employee.period'].create({
            'start_date': start_date,
            'end_date': end_date,
            'balance': balance,
            'previous_balance': previous_balance,
            'lost': 0,
            'employee_id': employee_id,
            'continuous_cap': continuous_cap,
            'origin': origin
        })
