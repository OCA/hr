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

from .hr_employee_benefit_rate import get_amount_types


class HrEmployeeBenefit(models.Model):
    """Employee Benefit"""

    _name = 'hr.employee.benefit'
    _description = _(__doc__)

    contract_id = fields.Many2one(
        'hr.contract',
        'Contract',
        ondelete='cascade',
        index=True,
    )
    category_id = fields.Many2one(
        'hr.employee.benefit.category',
        'Benefit',
        required=True,
        ondelete='cascade',
        index=True,
    )
    rate_id = fields.Many2one(
        'hr.employee.benefit.rate',
        'Rate',
        required=True,
    )
    employee_amount = fields.Float(
        related='rate_id.employee_amount',
        string='Employee Amount',
        readonly=True,
    )
    employer_amount = fields.Float(
        related='rate_id.employer_amount',
        string='Employer Amount',
        readonly=True,
    )
    amount_type = fields.Selection(
        get_amount_types,
        related='rate_id.amount_type',
        string="Amount Type",
        readonly=True,
    )
    date_start = fields.Date(
        'Start Date', required=True,
        default=fields.Date.context_today,
    )
    date_end = fields.Date('End Date')
    code = fields.Char(
        related='category_id.code',
        string='Code',
    )

    @api.one
    @api.constrains('category_id', 'rate_id')
    def _check_category_id(self):
        """
        Checks that the category on the benefit and the rate
        is the same
        """
        if not self.category_id == self.rate_id.category_id:
            raise ValidationError(
                _('You must select a rate related to the '
                  'selected category.'))

    @api.one
    def compute_amounts(self, payslip):
        if (
            self.date_start <= payslip.date_from and
            not (self.date_end and payslip.date_to > self.date_end)
        ):
            self.rate_id.compute_amounts(payslip)
