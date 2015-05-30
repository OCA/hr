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
from .hr_employee_benefit_rate import get_amount_types


class HrEmployeeBenefit(orm.Model):
    _name = 'hr.employee.benefit'
    _description = 'Employee Benefit'

    def compute_amounts(self, cr, uid, ids, payslip, context=None):
        date_from = payslip.date_from
        date_to = payslip.date_to
        for benefit in self.browse(cr, uid, ids, context=context):
            if (
                benefit.date_start <= date_from and
                (not benefit.date_end or date_to <= benefit.date_end)
            ):
                benefit.rate_id.compute_amounts(payslip)

    _columns = {
        'contract_id': fields.many2one(
            'hr.contract',
            'Contract',
            ondelete='cascade',
            select=True
        ),
        'category_id': fields.many2one(
            'hr.employee.benefit.category',
            'Benefit',
            required=True,
            ondelete='cascade',
            select=True
        ),
        'rate_id': fields.many2one(
            'hr.employee.benefit.rate',
            'Rate',
            required=True,
        ),
        'employee_amount': fields.related(
            'rate_id',
            'employee_amount',
            type='float',
            string='Employee Amount',
            readonly=True,
        ),
        'employer_amount': fields.related(
            'rate_id',
            'employer_amount',
            type='float',
            string='Employer Amount',
            readonly=True,
        ),
        'amount_type': fields.related(
            'rate_id',
            'amount_type',
            selection=get_amount_types,
            string="Amount Type",
            type="selection",
            readonly=True,
        ),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'code': fields.related(
            'category_id',
            'code',
            type='char',
            string='Code'
        ),
    }

    def _check_category_id(self, cr, uid, ids, context=None):
        """
        Checks that the category on the benefit and the rate
        is the same
        """
        for benefit in self.browse(cr, uid, ids, context):

            if not benefit.category_id == benefit.rate_id.category_id:
                return False

        return True

    _constraints = [(
        _check_category_id,
        'Error! You must select a rate related to the selected category.',
        ['category_id', 'rate_id']
    )]
