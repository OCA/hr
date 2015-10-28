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

from openerp import fields, models, _
import openerp.addons.decimal_precision as dp

from .hr_employee_benefit_rate import get_amount_types


class HrEmployeeBenefitRateLine(models.Model):
    """Employee Benefit Rate Line"""

    _name = 'hr.employee.benefit.rate.line'
    _description = _(__doc__)

    employee_amount = fields.Float(
        'Employee Amount',
        required=True,
        digits_compute=dp.get_precision('Payroll'),
    )
    employer_amount = fields.Float(
        'Employer Amount',
        required=True,
        digits_compute=dp.get_precision('Payroll'),
    )
    date_start = fields.Date(
        'Start Date',
        required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date('End Date')
    parent_id = fields.Many2one(
        'hr.employee.benefit.rate',
        'Parent',
        ondelete='cascade',
        required=True,
    )
    amount_type = fields.Selection(
        get_amount_types,
        related='parent_id.amount_type',
        string="Amount Type",
        readonly=True,
    )
    category_id = fields.Many2one(
        'hr.employee.benefit.category',
        related='parent_id.category_id',
        string="Category",
        readonly=True,
    )

    _order = 'date_start desc'
