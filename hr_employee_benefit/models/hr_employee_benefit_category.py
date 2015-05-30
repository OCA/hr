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


class HrEmployeeBenefitCategory(orm.Model):
    _name = 'hr.employee.benefit.category'
    _description = 'Category of employee benefits'
    _columns = {
        'name': fields.char('Benefit Name', required=True),
        'code': fields.char(
            'Code', required=True, help=""
            "The code that can be used in the salary rules to identify "
            "the benefit",
        ),
        'description': fields.text(
            'Description',
            required=True,
            help="Brief explanation of which benefits the category contains."
        ),

        'salary_rule_ids': fields.many2many(
            'hr.salary.rule', 'salary_rule_employee_benefit_rel',
            'benefit_id', 'salary_rule_id', 'Salary Rules',
        ),

        'rate_ids': fields.one2many(
            'hr.employee.benefit.rate',
            'category_id',
            string="Benefit Rates",
        ),

        # Field used to enter an external identifier for a benefit category
        # Example, pension plans may have a registration number
        'reference': fields.char('Reference'),
        'active': fields.boolean('active'),

    }

    _defaults = {
        'active': True,
    }
