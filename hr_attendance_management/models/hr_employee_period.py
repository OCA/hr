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

    start_date = fields.Date(string='First date of period')
    end_date = fields.Date(string='Last date of period (exclusive)')
    end_date_display = fields.Date(string="Last date of period",
                                   compute="_compute_display_of_end_date")
    balance = fields.Float(string='Balance of period')
    final_balance = fields.Float(string="Total balance at end of period",
                                 compute='_compute_final_balance',
                                 readonly=True,
                                 store=True)
    previous_period = fields.Many2one('hr.employee.period',
                                      string="Previous period",
                                      readonly=True)
    lost = fields.Float(string='Hours lost', readonly=True)
    employee_id = fields.Many2one("hr.employee", string='Employee', readonly=True)
    continuous_cap = fields.Boolean(string='Continuous cap for this period')

    @api.depends('end_date')
    def _compute_display_of_end_date(self):
        for period in self:
            if period.end_date:
                period.end_date_display = datetime.datetime.strptime(period.end_date, '%Y-%m-%d') \
                                          - datetime.timedelta(days=1)

    @api.depends('previous_period.final_balance', 'balance')
    def _compute_final_balance(self):
        for period in self:
            period.final_balance = period.update_past_period().final_balance

    def update_past_period(self):
        """
        This function recompute balance and lost hours for one period.
        :return:
        """
        for current_period in self:
            return current_period.calculate_and_write_final_balance()

    def calculate_and_write_final_balance(self):
        start_date = self.start_date
        end_date = self.end_date
        previous_balance = None
        balance_of_period = self.balance

        if self.previous_period:
            previous_balance = self.previous_period.final_balance
        else:
            previous_balance = self.employee_id.initial_balance

        extra, lost = self.employee_id.past_balance_computation(
            start_date=start_date,
            end_date=end_date,
            existing_balance=previous_balance)

        final_balance = extra
        computed_balance = extra - previous_balance
        # the balance of the period was modified by an user
        if abs(balance_of_period - computed_balance) > 0.1:
            final_balance = final_balance + balance_of_period - computed_balance

        if abs(self.final_balance - final_balance) > 0.1:
            self.final_balance = final_balance
            self.write({
                'final_balance': final_balance
            })

        if self.balance == 0:
            self.balance = extra - previous_balance
            self.write({
                'balance': extra - previous_balance
            })

        return self

    @api.multi
    def create(self, vals):
        res = super(HrEmployeePeriod, self).create(vals)

        start_date = vals['start_date']
        end_date = vals['end_date']

        origin = None
        if 'origin' in vals:
            origin = vals['origin']

        if end_date and start_date and not origin == "override":

            employee = res.employee_id
            if not employee:
                employee = self.env['hr.employee'].search([
                    ('employee_id', '=', vals['employee_id'])
                ])
            employee_periods = employee.period_ids

            # last period before start_date
            previous_period = None
            previous_periods = employee_periods.filtered(
                lambda r: r.end_date <= start_date
            ).sorted(key=lambda r: r.start_date)
            if previous_periods:
                previous_period = previous_periods[-1]

            # period that begins before and finish after start_date
            previous_overlapping_period = employee_periods.filtered(
                lambda r: end_date > r.end_date > start_date and r.start_date < start_date)

            # period that begins before and finish after end_date
            next_overlapping_period = employee_periods.filtered(
                lambda r: end_date > r.start_date > start_date and r.end_date > end_date)

            # period that begins before start_date and finish after end_date
            surrounding_period = employee_periods.filtered(
                lambda r: r.start_date < start_date and r.end_date > end_date)

            # period that is inside the new one
            surrounded_periods = employee_periods.filtered(
                lambda r: start_date <= r.start_date < end_date and start_date < r.end_date <= end_date
                and r.id != res.id
            )

            if isinstance(start_date, basestring):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')

            if isinstance(end_date, basestring):
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

            # We want to create a period inside another one
            if surrounding_period:
                surround_start = surrounding_period.start_date
                surround_end = surrounding_period.end_date
                surround_continuous_cap = surrounding_period.continuous_cap
                surround_period_previous_period_id = surrounding_period.previous_period.id
                employee_id = surrounding_period.employee_id
                surrounding_period.unlink()

                # Creates a period from the beginning of the surrounding period
                # to the beginning of the new period
                period1 = self.create_period(start_date=surround_start,
                                             end_date=start_date,
                                             employee_id=employee_id.id,
                                             balance=0,
                                             previous_period=surround_period_previous_period_id,
                                             continuous_cap=surround_continuous_cap,
                                             origin="override")

                res.write({
                    'previous_period': period1.id
                })

                # Creates a period from the end of the new period
                # to the end of the surrounding period
                self.create_period(start_date=end_date,
                                   end_date=surround_end,
                                   employee_id=employee_id.id,
                                   balance=0,
                                   previous_period=res.id,
                                   continuous_cap=surround_continuous_cap,
                                   origin="override")

                period1.update_past_period()
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
                                                    previous_period=previous_period.id,
                                                    continuous_cap=self.employee_id.extra_hours_continuous_cap,
                                                    origin="override")

                        res.write({
                            'previous_period': period.id
                        })
                        period.update_past_period()

                    res.write({
                        'previous_period': previous_period.id
                    })
                if previous_overlapping_period:
                    # Modify first previous overlapping period
                    previous_overlapping_period.write({
                        'end_date': start_date
                    })
                    res.write({
                        'previous_period': previous_overlapping_period.id
                    })
                    previous_overlapping_period.update_past_period()

                # A following period overlap with the new one
                if next_overlapping_period:
                    # Modify next overlapping period
                    next_overlapping_period.write({
                        'start_date': end_date,
                        'previous_period': res.id
                    })
                    # next_overlapping_period.update_past_period()

                if surrounded_periods:
                    for period in surrounded_periods:
                        # deletes useless period
                        period.unlink()

                res = res.update_past_period()
        return res

    def create_period(self, start_date, end_date, employee_id, balance,
                      previous_period, continuous_cap, origin):
        return self.env['hr.employee.period'].create({
            'start_date': start_date,
            'end_date': end_date,
            'balance': balance,
            'previous_period': previous_period,
            'lost': 0,
            'employee_id': employee_id,
            'continuous_cap': continuous_cap,
            'origin': origin
        })
