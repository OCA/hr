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
from openerp.tools.translate import _


def get_amount_types(self, cr, uid, context=None):
    return [
        ('cash', _('Cash')),
        ('hours', _('Hours')),
    ]


class hr_holidays_status_accrual_line(orm.Model):
    """
    The lines that will be added to an employee's leave accrual
    when a payslip is computed

    If substract field is True, the amount related to the salary rule
    will be substracted from the accrual instead of added to it.
    """
    _name = 'hr.holidays.status.accrual.line'
    _description = 'Holidays Status Accrual Line'
    _columns = {
        'leave_type_id': fields.many2one(
            'hr.holidays.status',
            'Leave Type',
            required=True,
        ),
        'salary_rule_id': fields.many2one(
            'hr.salary.rule',
            'Salary Rule',
        ),
        'substract': fields.boolean(
            'Substract Amount',
        ),
        'amount_type': fields.selection(
            get_amount_types,
            string="Amount Type",
        ),
    }

    _defaults = {
        'substract': False,
        'amount_type': 'cash',
    }
