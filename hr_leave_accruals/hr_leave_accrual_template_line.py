# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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

from openerp.osv import orm, fields


class hr_leave_accrual_template_line(orm.Model):
    """
    The lines that will be added to an employee's leave accrual
    when a payslip is computed

    If substract field is True, the amount related to the salary rule
    will be substracted from the accrual instead of added to it.
    """
    _name = 'hr.leave.accrual.template.line'
    _description = 'Leave Accrual Template Line'
    _columns = {
        'template_id': fields.many2one(
            'hr.leave.accrual.template',
            'Leave Accrual Template',
            required=True,
        ),
        'salary_rule_id': fields.many2one(
            'hr.salary.rule',
            'Salary Rule',
        ),
        'substract': fields.boolean(
            'Substract Amount',
        )
    }
    _defaults = {
        'substract': False,
    }
