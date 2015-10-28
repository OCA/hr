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


class HrEmployeeBenefitCategory(models.Model):
    """Employee Benefit Category"""

    _name = 'hr.employee.benefit.category'
    _description = _(__doc__)

    name = fields.Char('Benefit Name', required=True)
    code = fields.Char(
        'Code',
        help="The code that can be used in the salary rules to identify "
        "the benefit",
    )
    description = fields.Text(
        'Description',
        help="Brief explanation of which benefits the category contains."
    )
    salary_rule_ids = fields.Many2many(
        'hr.salary.rule', 'salary_rule_employee_benefit_rel',
        'benefit_id', 'salary_rule_id', 'Salary Rules',
    )
    rate_ids = fields.One2many(
        'hr.employee.benefit.rate',
        'category_id',
        string="Benefit Rates",
    )
    reference = fields.Char(
        'Reference',
        help="Field used to enter an external identifier for a "
        "benefit category. Example, pension plans may have a "
        "registration number."
    )
    active = fields.Boolean('active', default=True)
