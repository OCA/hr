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

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from itertools import permutations
from datetime import datetime
strptime = datetime.strptime


def get_amount_types(self, cr, uid, context=None):
    """ Proxy function used to query rate types from any model
    """
    return self.pool['hr.employee.benefit.rate'].get_all_amount_types(
        cr, uid, context=context)


class HrEmployeeBenefitRate(orm.Model):
    _name = 'hr.employee.benefit.rate'
    _decription = 'Employee Benefit Rate'

    def get_all_amount_types(self, cr, uid, context=None):
        """ Get the list of amount types for employee benefits
        This method is not called directly so that it can be inherited
        easily in other modules. When inheriting this method, the list
        of selections is updated in every related models.
        """
        return [
            ('each_pay', _('Each Pay')),
            ('annual', _('Annual')),
        ]

    def _get_amounts_now(self, cr, uid, ids, field_names, arg, context=None):
        res = {}
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        for rate in self.browse(cr, uid, ids, context=context):
            res[rate.id] = {
                'employee_amount': rate.get_amount(today),
                'employer_amount': rate.get_amount(
                    today, employer=True),
            }
        return res

    def get_amount(self, cr, uid, ids, date, employer=False, context=None):
        rate = self.browse(cr, uid, ids[0], context=context)
        for line in rate.line_ids:
            if line.date_start <= date and (
                not line.date_end or date <= line.date_end
            ):
                return employer and line.employer_amount or \
                    line.employee_amount
        return False

    def _get_line_base_ratio(self, cr, uid, line, payslip, context=None):
        """ Ratio by which to multiply the rate to get the amount for
        the current payslip
        """
        ratio = 1.0

        if line.amount_type == 'annual':
            ratio /= payslip.pays_per_year

        return ratio

    def _get_line_duration_ratio(
        self, cr, uid, line, date_from, date_to, duration, context=None
    ):
        """ The duration ratio is a factor to multiply a rate that
        overlaps partially a payslip's duration
        """
        # Case where the benefit begins after the payslip period
        # begins.
        date_start = strptime(line.date_start, DEFAULT_SERVER_DATE_FORMAT)
        start_offset = max((date_start - date_from).days, 0)

        # Case where the benefit ends before the payslip period ends.
        date_end = line.date_end and strptime(
            line.date_end, DEFAULT_SERVER_DATE_FORMAT)

        end_offset = date_end and max(
            (date_to - date_end).days, 0) or 0

        duration_ratio = 1 - float(
            start_offset + end_offset) / duration

        return duration_ratio

    def compute_amounts(
        self, cr, uid, ids, payslip, context=None
    ):
        """ Compute benefit lines
        """
        date_from = strptime(payslip.date_from, DEFAULT_SERVER_DATE_FORMAT)
        date_to = strptime(payslip.date_to, DEFAULT_SERVER_DATE_FORMAT)
        duration = (date_to - date_from).days + 1

        for rate in self.browse(cr, uid, ids, context=context):

            rate_lines = [
                line for line in rate.line_ids
                if (
                    not line.date_end or payslip.date_from <= line.date_end
                ) and line.date_start <= payslip.date_to
            ]

            for line in rate_lines:
                base_ratio = self._get_line_base_ratio(
                    cr, uid, line, payslip, context=context)

                duration_ratio = self._get_line_duration_ratio(
                    cr, uid, line, date_from, date_to, duration,
                    context=context)

                ratio = base_ratio * duration_ratio

                self.pool['hr.payslip.benefit.line'].create(
                    cr, uid, {
                        'payslip_id': payslip.id,
                        'employer_amount': ratio * line.employer_amount,
                        'employee_amount': ratio * line.employee_amount,
                        'category_id': line.category_id.id,
                        'source': 'contract',
                        'reference': line.category_id.reference,
                    }, context=context)

    _columns = {
        'category_id': fields.many2one(
            'hr.employee.benefit.category',
            'Benefit Category',
            required=True,
        ),
        'name': fields.char('Name', required=True),
        'line_ids': fields.one2many(
            'hr.employee.benefit.rate.line',
            'parent_id',
            'Rates',
        ),
        'amount_type': fields.selection(
            get_amount_types,
            required=True,
            string="Amount Type",
        ),
        'employee_amount': fields.function(
            _get_amounts_now,
            type='float',
            string='Employee Contribution',
            multi=True,
            readonly=True,
        ),
        'employer_amount': fields.function(
            _get_amounts_now,
            type='float',
            string='Employer Contribution',
            multi=True,
            readonly=True,
        ),
    }

    _defaults = {
        'amount_type': 'each_pay',
    }

    def _check_overlapping_rates(self, cr, uid, ids, context=None):
        """
        Checks if a rate has two lines that overlap in time.
        """
        for rate in self.browse(cr, uid, ids, context):

            for r1, r2 in permutations(rate.line_ids, 2):
                if r1.date_end and (
                        r1.date_start <= r2.date_start <= r1.date_end):
                    return False
                elif not r1.date_end and (r1.date_start <= r2.date_start):
                    return False

        return True

    _constraints = [(
        _check_overlapping_rates,
        'Error! You cannot have overlapping rates',
        ['line_ids']
    )]
