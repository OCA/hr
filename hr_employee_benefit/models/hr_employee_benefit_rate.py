# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import api, fields, models, _
from openerp.exceptions import ValidationError
from itertools import permutations
from datetime import datetime
strptime = datetime.strptime

context_today = fields.Date.context_today
from_string = fields.Date.from_string


def get_amount_types(self):
    """
    Proxy function used to query rate types from any model
    """
    return self.env['hr.employee.benefit.rate'].get_all_amount_types()


class HrEmployeeBenefitRate(models.Model):
    """Employee Benefit Rate"""

    _name = 'hr.employee.benefit.rate'
    _description = _(__doc__)

    category_id = fields.Many2one(
        'hr.employee.benefit.category',
        'Benefit Category',
        required=True,
    )
    name = fields.Char('Name', required=True)
    line_ids = fields.One2many(
        'hr.employee.benefit.rate.line',
        'parent_id',
        'Rates',
    )
    amount_type = fields.Selection(
        get_amount_types,
        required=True,
        string="Amount Type",
        default='each_pay',
    )
    employee_amount = fields.Float(
        compute='_get_amounts_now',
        string='Employee Contribution',
        readonly=True,
    )
    employer_amount = fields.Float(
        compute='_get_amounts_now',
        string='Employer Contribution',
        readonly=True,
    )

    @api.one
    @api.constrains('line_ids')
    def _check_overlapping_rates(self):
        """
        Checks if a rate has two lines that overlap in time.
        """
        for r1, r2 in permutations(self.line_ids, 2):
            if (
                r1.date_end and
                r1.date_start <= r2.date_start <= r1.date_end
            ) or (
                not r1.date_end and
                r1.date_start <= r2.date_start
            ):
                raise ValidationError(
                    _('You cannot have overlapping rates'))

    @api.model
    def get_all_amount_types(self):
        """
        Get the list of amount types for employee benefits
        This method is not called directly so that it can be inherited
        easily in other modules. When inheriting this method, the list
        of selections is updated in every related models.
        """
        return [
            ('each_pay', _('Each Pay')),
            ('annual', _('Annual')),
        ]

    @api.multi
    def _get_amounts_now(self):
        today = context_today(self)
        for rate in self:
            rate.employee_amount = rate.get_amount(today)
            rate.employer_amount = rate.get_amount(today, employer=True)

    @api.multi
    def get_amount(self, date, employer=False):
        self.ensure_one()
        for line in self.line_ids:
            if line.date_start <= date and (
                not line.date_end or date <= line.date_end
            ):
                return (
                    line.employer_amount if employer else
                    line.employee_amount
                )
        return False

    @api.model
    def _get_line_base_ratio(self, line, payslip):
        """
        Ratio by which to multiply the rate to get the amount for
        the current payslip
        """
        ratio = 1.0

        if line.amount_type == 'annual':
            ratio /= payslip.pays_per_year

        return ratio

    @api.model
    def _get_line_duration_ratio(
        self, line, date_from, date_to, duration
    ):
        """
        The duration ratio is a factor to multiply a rate that
        overlaps partially a payslip's duration
        """
        # Case where the benefit begins after the payslip period
        # begins.
        date_start = from_string(line.date_start)
        start_offset = max((date_start - date_from).days, 0)

        # Case where the benefit ends before the payslip period ends.
        date_end = line.date_end and from_string(line.date_end)

        end_offset = date_end and max(
            (date_to - date_end).days, 0) or 0

        duration_ratio = 1 - float(
            start_offset + end_offset) / duration

        return duration_ratio

    @api.multi
    def compute_amounts(self, payslip):
        """
        Compute benefit lines
        """
        date_from = from_string(payslip.date_from)
        date_to = from_string(payslip.date_to)
        duration = (date_to - date_from).days + 1

        line_obj = self.env['hr.payslip.benefit.line']

        rate_lines = [
            line for line in self.line_ids
            if (
                not line.date_end or payslip.date_from <= line.date_end
            ) and line.date_start <= payslip.date_to
        ]

        for line in rate_lines:
            base_ratio = self._get_line_base_ratio(line, payslip)

            duration_ratio = self._get_line_duration_ratio(
                line, date_from, date_to, duration)

            ratio = base_ratio * duration_ratio

            line_obj.create({
                'payslip_id': payslip.id,
                'employer_amount': ratio * line.employer_amount,
                'employee_amount': ratio * line.employee_amount,
                'category_id': line.category_id.id,
                'source': 'contract',
                'reference': line.category_id.reference,
            })
