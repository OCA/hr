# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
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


class hr_salary_rule_variable(orm.Model):
    _name = 'hr.salary.rule.variable'
    _description = 'Variables used on salary rules that change over the years'
    _columns = {
        'salary_rule_id': fields.many2one(
            'hr.salary.rule',
            'Salary Rule',
            ondelete='cascade',
            required=True,
        ),
        'date_from': fields.date(
            'Date From',
            required=True,
        ),
        'date_to': fields.date(
            'Date To',
        ),
        'type': fields.selection(
            [
                ('python', 'Python Code'),
                ('fixed', 'Fixed Amount')
            ],
            string='Type'
        ),
        'python_code': fields.text(
            'Python Code'
        ),
        'fixed_amount': fields.float(
            'Fixed Amount'
        ),
    }
