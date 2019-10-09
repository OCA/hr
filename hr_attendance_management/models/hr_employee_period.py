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

    start_date = fields.Date(string='First date of period')
    end_date = fields.Date(string='Date of balance computation')
    balance = fields.Float(string='Hours balance at the date of computation', readonly=True)
    previous_balance = fields.Float(string='Balance of previous period', readonly=True)
    lost = fields.Float(string='Hours lost at the date of computation', readonly=True)
    employee_id = fields.Many2one("hr.employee", string='Employee', readonly=True)
    continuous_cap = fields.Boolean(string='Continuous cap for this period')

    @api.multi
    def write(self, vals):
        res = super(HrEmployeePeriod, self).write(vals)
        for period in self:
            if 'continuous_cap' in vals or 'end_date' in vals or 'start_date' in vals:
                previous_period = self.env['hr.employee.period'].search([
                    ('employee_id', '=', period.employee_id.id),
                    ('end_date', '<', period.start_date)
                ], order='end_date desc', limit=1)
                config = self.env['base.config.settings'].create({})
                config.set_beginning_date()
                start_date = None
                end_date = period.end_date
                balance = None

                if previous_period:
                    start_date = datetime.datetime.strptime(previous_period.end_date, '%Y-%m-%d') + \
                                 datetime.timedelta(days=1)
                    balance = previous_period.balance
                    if 'start_date' in vals:
                        start_date = vals['start_date']
                    elif 'end_date' in vals:
                        end_date = vals['end_date']
                else:
                    start_date = config.get_beginning_date_for_balance_computation()
                    balance = period.employee_id.initial_balance

                period.employee_id.update_past_periods(start_date,
                                                       end_date,
                                                       balance)
        return res

    @api.multi
    def create(self, vals):
        res = super(HrEmployeePeriod, self).create(vals)

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
                ('end_date', '<', start_date)
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
                # to just before the beginning of the new period
                self.create_period(start_date=surround_start,
                                   end_date=start_date - datetime.timedelta(days=1),
                                   employee_id=employee_id.id,
                                   balance=0,
                                   previous_balance=balance_previous,
                                   continuous_cap=surround_continuous_cap,
                                   origin="override")

                # Creates a period from just after the end of the new period
                # to the end of the surrounding period
                self.create_period(start_date=end_date + datetime.timedelta(days=1),
                                   end_date=surround_end,
                                   employee_id=employee_id.id,
                                   balance=0,
                                   previous_balance=0,
                                   continuous_cap=surround_continuous_cap,
                                   origin="override")

                employee.update_past_periods(surround_start, start_date - datetime.timedelta(days=1), balance_previous)

            else:
                if previous_period:
                    previous_end_date = datetime.datetime.strptime(previous_period.end_date, '%Y-%m-%d')
                    # Periods not overlapping and with the space for a new one
                    if not previous_overlapping_period and (start_date - previous_end_date).days > 1:
                        # Creates period between previous_period.end_date and start_date of new one
                        self.create_period(start_date=previous_end_date + datetime.timedelta(days=1),
                                           end_date=start_date - datetime.timedelta(days=1),
                                           employee_id=previous_period.employee_id.id,
                                           balance=0,
                                           previous_balance=previous_period.balance,
                                           continuous_cap=self.employee_id.extra_hours_continuous_cap,
                                           origin="override")

                        employee.update_past_periods(previous_end_date + datetime.timedelta(days=1),
                                                     start_date - datetime.timedelta(days=1),
                                                     previous_period.balance)

                if previous_overlapping_period:
                    # Modify first previous overlapping period
                    previous_overlapping_period.write({
                        'end_date': start_date - datetime.timedelta(days=1)
                    })

                # A following period overlap with the new one
                if next_overlapping_period:
                    # Modify next overlapping period
                    next_overlapping_period.write({
                        'start_date': end_date + datetime.timedelta(days=1)
                    })

                else:
                    employee.update_past_periods(start_date,
                                                 end_date,
                                                 employee.initial_balance)

        return res

    def create_period(self, start_date, end_date, employee_id, balance, previous_balance, continuous_cap, origin):
        self.env['hr.employee.period'].create({
            'start_date': start_date,
            'end_date': end_date,
            'balance': balance,
            'previous_balance': previous_balance,
            'lost': 0,
            'employee_id': employee_id,
            'continuous_cap': continuous_cap,
            'origin': origin
        })
