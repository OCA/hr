# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from datetime import date, timedelta

from openerp import models, fields, api
from openerp.exceptions import Warning as UserWarning


class HrHolidaysEvaluationRuleset(models.Model):
    _name = 'hr.holidays.evaluation.ruleset'

    name = fields.Char(required=True)
    mode = fields.Selection(
        [
            ('first', 'First'),
            ('max', 'Largest'),
            ('min', 'Minimum')
        ],
        'Evaluation Mode',
        default='first',
        required=True,
        help="Defines what to do if multiple rules in this ruleset evaluates "
             "to true.\n * Consider only the first to evaluate.\n * Consider "
             "the one with the largest return value.\n * COnsider the one "
             "with the smallest return value."
    )
    period = fields.Selection(
        [
            ('year', 'Start of Year'),
            ('anniversary', 'Employment Anniversary'),
        ],
        'Period Definition',
        default='year',
        required=True,
        help="Defines what concept of leave period should be used for "
             "tracking taken holidays.\n * Start of the year will consider "
             "every new year as the start of a new leave period.\n *  "
             "Employment Anniversary will use the anniversary of employee's "
             "employment"
    )
    active = fields.Boolean(default=True)
    rule_ids = fields.One2many(
        'hr.holidays.evaluation.rule',
        'ruleset_id',
        'Allocation Rules'
    )

    @api.multi
    def evaluate_allocation(self, employee, dt=None):
        """
        evaluates employee's maximum allocation at a given time
        @param employee: employee for whom we need to evaluate allocation
        @param dt: date object that allows also to compute allocation at a
                   point in time rather than just now
        """
        self.ensure_one()
        dt = dt or date.today()
        # let's pass this in so that employee service length is computed
        # at our reference date
        employee = employee.with_context(date_now=dt)
        localdict = dict(
            employee=employee,
            contract=employee.contract_id,
            job=employee.job_id,
            date_ref=dt,
            result=None,
        )
        rules_matched_days = []
        for rule in self.rule_ids:
            if rule.satisfy_condition(localdict):
                rules_matched_days.append(rule.amount)
                if self.mode == 'first':
                    break
        if not rules_matched_days:
            return 0
        if self.mode == 'min':
            return min(rules_matched_days)
        elif self.mode == 'max':
            return max(rules_matched_days)
        else:
            return rules_matched_days[0]

    @api.multi
    def evaluate_withdrawals(self, holiday_status, employee, dt=None):
        """
        evaluates number of leaves taken in a given period
        @param holiday_status: holiday status to evaluate for
        @param employee: employee for whom we need to evaluate withdrawals
        @param dt: date object that allows also to compute withdrawals at a
                   point in time rather than just now
        """
        self.ensure_one()
        dt = dt or date.today()
        period_start, period_end = self.holidays_period(employee, dt)
        domain = [
            ('state', '=', 'validate'),
            ('date_from', '>=', str(period_start)),
            ('date_from', '<=', str(period_end)),
            ('type', '=', 'remove'),
            ('employee_id', '=', employee.id),
            ('holiday_status_id', '=', holiday_status.id)
        ]
        leaves = self.env['hr.holidays'].search(domain)
        return sum(leaves.mapped('number_of_days'))

    @api.multi
    def evaluate_remaining(self, employee, dt=None):
        """
        self.ensure_one()
        evaluates how much leave employee is entitled to
        @param employee: employee for whom we need to evaluate remaining
        @param dt: date object that allows also to compute remaining at a
                   point in time rather than just now
        """
        dt = dt or date.today()
        return (self.evaluate_allocation(employee, dt) -
                self.evaluate_withdrawals(employee, dt))

    def holidays_period(self, employee, dt=None):
        """
        Calculates the start and end date of an employee's leave period taking
        into consideration this ruleset's definition of that a leave period is
        @param employee: employee object
        @param dt: if supplied it gives the leave period pounding that date
        @return: tuple of date objects (period_start, period_end)
        """
        dt = dt or date.today()
        employee_start_dt = fields.Date.from_string(employee.date_start)
        if employee_start_dt and employee_start_dt > dt:
            raise UserWarning('Reference date should not be before '
                              'employee\'s employment date')

        if self.period == 'anniversary':
            one_day_before = employee_start_dt - timedelta(days=1)
            return (
                date(dt.year, employee_start_dt.month, employee_start_dt.day),
                date(dt.year + 1, one_day_before.month, one_day_before.day)
            )
        else:
            return (date(dt.year, 01, 01), date(dt.year, 12, 31))
