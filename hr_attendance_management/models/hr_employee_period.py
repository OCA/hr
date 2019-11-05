# -*- coding: utf-8 -*-

# Copyright (C) 2018 Compassion CH
# Author: Quentin Gigon <gigon.quentin@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import datetime
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


##########################################################################
#                             STATIC METHODS                             #
##########################################################################

def get_previous_period(employee_periods, res):
    previous_period = None
    previous_periods = employee_periods.filtered(
        lambda r: r.end_date <= res.start_date)\
        .sorted(key=lambda r: r.start_date)
    if previous_periods:
        previous_period = previous_periods[-1]
    return previous_period


def get_previous_overlapping_period(employee_periods, res):
    return employee_periods.filtered(
        lambda r: res.end_date >= r.end_date > res.start_date
        and r.start_date < res.start_date)


def get_next_overlapping_period(employee_periods, res):
    return employee_periods.filtered(
        lambda r: res.end_date > r.start_date > res.start_date
        and r.end_date >= res.end_date)


def get_surrounding_period(employee_periods, res):
    return employee_periods.filtered(
        lambda r: r.start_date < res.start_date
        and r.end_date > res.end_date)


def get_surrounded_periods(employee_periods, res):
    return employee_periods.filtered(
        lambda r: res.start_date <= r.start_date < res.end_date
        and res.start_date < r.end_date <= res.end_date
        and r.id != res.id)


class HrEmployeePeriod(models.Model):
    """
      This class represent a period of work of an employee.
      It contains the balance of hours between the start_date and end_date
      and also the final_balance of the employee at the end_date.
      Periods are linked together as a LinkedList, where a period has
      a reference to its previous_period (None if first period)
      and an update to one period will update subsequently all
      following periods.
      """
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
                period.end_date_display = \
                    datetime.datetime.strptime(period.end_date, '%Y-%m-%d') - \
                    datetime.timedelta(days=1)

    @api.depends('previous_period.final_balance')
    def _compute_final_balance(self):
        for period in self:
            period.final_balance = period.update_period(origin="compute")

    def update_period(self, origin=None):
        """
        This function update balance and final_balance for a period.
        It must be called if the final_balance of the previous period
        has been changed or if the balance of the current period was changed.
        :param origin: Origin of the call
        :return: the current period after modification
        """
        for current_period in self:
            balance, final_balance = \
                current_period.calculate_balance_and_final_balance()

            # If we come for the compute_final_balance method,
            # don't write but just return value. Else we
            # have error with recursion
            if origin == "compute":
                return final_balance
            else:
                current_period.write({
                    'balance': balance,
                    'final_balance': final_balance
                })
                return current_period

    def calculate_balance_and_final_balance(self):
        """
        This function recompute balance and final_balance for a period.
        :return: the balance and final balance of the current period
        """
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

        balance = extra - previous_balance

        return balance, final_balance

    @api.multi
    def create(self, vals):
        res = super(HrEmployeePeriod, self).create(vals)

        start_date = vals['start_date']
        end_date = vals['end_date']

        if str(start_date) >= str(end_date):
            return ValueError("The end_date cannot be smaller than the start_date")

        origin = None
        if 'origin' in vals:
            origin = vals['origin']

        if end_date and start_date and not origin == "create":

            period_to_update = None

            employee = res.employee_id
            if not employee:
                employee = self.env['hr.employee'].search([
                    ('id', '=', vals['employee_id'])
                ])
            employee_periods = employee.period_ids

            # last period before start_date
            previous_period = get_previous_period(employee_periods, res)

            # period that begins before and finish after start_date
            previous_overlapping_period = \
                get_previous_overlapping_period(employee_periods, res)

            # period that begins before and finish after end_date
            next_overlapping_period = \
                get_next_overlapping_period(employee_periods, res)

            # period that begins before start_date and finish after end_date
            surrounding_period = get_surrounding_period(employee_periods, res)

            # period that is inside the new one
            surrounded_periods = get_surrounded_periods(employee_periods, res)

            # Convert start and end dates to dates if they are strings
            if isinstance(start_date, str):
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')

            # We want to create a period inside another one
            if surrounding_period:
                self.handle_surrounding_period(
                    surrounding_period, start_date, end_date, res
                )
            else:
                # We must modify end_date of previous period
                # and maybe create 1 more between the 2
                if previous_period:
                    self.handle_previous_period(
                        previous_period, previous_overlapping_period, start_date, res
                    )
                    period_to_update = previous_period

                    # A previous period overlaps with the new one
                if previous_overlapping_period:
                    self.handle_previous_overlapping_period(
                        previous_overlapping_period, start_date, res
                    )
                    period_to_update = previous_overlapping_period

                # A following period overlap with the new one
                if next_overlapping_period:
                    self.handle_next_overlapping_period(
                        next_overlapping_period, end_date, res.id
                    )
                    period_to_update = res

            if surrounded_periods:
                for period in surrounded_periods:
                    # deletes useless period
                    period.unlink()
            if period_to_update:
                period_to_update.update_period()
            # employee.period_ids.sorted(key=lambda p: p.start_date)[0].update_period(origin="test")
            res = res.update_period()
        return res

    def handle_previous_period(self, previous_period, previous_overlapping_period,
                               start_date, res):
        previous_end_date = \
            datetime.datetime.strptime(previous_period.end_date, '%Y-%m-%d')
        # Periods not overlapping and with the space for a new one
        if not previous_overlapping_period \
                and (start_date - previous_end_date).days > 1:
            # Creates period between previous_period.end_date and start_date of new one
            period = self.create_period(start_date=previous_end_date,
                                        end_date=start_date,
                                        employee_id=previous_period.employee_id.id,
                                        balance=0,
                                        previous_period=previous_period.id,
                                        continuous_cap=
                                        self.employee_id.extra_hours_continuous_cap,
                                        origin="create")
            res.write({
                'previous_period': period.id
            })

            period.update_period()
            previous_period.update_period()
        else:
            res.write({
                'previous_period': previous_period.id
            })

    def handle_surrounding_period(self, surrounding_period, start_date, end_date, res):
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
                                     previous_period=
                                     surround_period_previous_period_id,
                                     continuous_cap=surround_continuous_cap,
                                     origin="create")

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
                           origin="create")

        period1.update_period()

    def handle_previous_overlapping_period(
            self, previous_overlapping_period, start_date, res):
        # Modify first previous overlapping period
        previous_overlapping_period.end_date = start_date
        res.write({
            'previous_period': previous_overlapping_period.id
        })

    def handle_next_overlapping_period(
            self, next_overlapping_period, end_date, res_id):
        # Modify next overlapping period
        next_overlapping_period.write({
            'start_date': end_date,
            'previous_period': res_id
        })

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
