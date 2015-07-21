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
from .hr_employee_benefit_rate import get_amount_types
import openerp.addons.decimal_precision as dp
import time


class HrEmployeeBenefitRateLine(orm.Model):
    _name = 'hr.employee.benefit.rate.line'
    _description = 'Employee Benefit Rate Line'
    _columns = {
        'employee_amount': fields.float(
            'Employee Amount',
            required=True,
            digits_compute=dp.get_precision('Payroll'),

        ),
        'employer_amount': fields.float(
            'Employer Amount',
            required=True,
            digits_compute=dp.get_precision('Payroll'),

        ),
        'date_start': fields.date(
            'Start Date',
            required=True,
        ),
        'date_end': fields.date('End Date'),
        'parent_id': fields.many2one(
            'hr.employee.benefit.rate',
            'Parent',
            ondelete='cascade',
            required=True,
        ),
        'amount_type': fields.related(
            'parent_id',
            'amount_type',
            selection=get_amount_types,
            string="Amount Type",
            type="selection",
            readonly=True,
        ),
        'category_id': fields.related(
            'parent_id',
            'category_id',
            string="Category",
            type="many2one",
            relation="hr.employee.benefit.category",
            readonly=True,
        ),
    }
    _defaults = {
        'date_start': lambda *a: time.strftime(DEFAULT_SERVER_DATE_FORMAT),
    }
    _order = 'date_start desc'
