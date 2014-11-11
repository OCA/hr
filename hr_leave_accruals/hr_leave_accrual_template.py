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


class hr_leave_accrual_template(orm.Model):
    """
    A leave accrual template represent a leave category
    e.g. Vacations, Sick Leaves, Compensatory, Legals, etc.

    Line_ids describe how the accrual must be computed in regard to an
    employee's payslip
    """
    _name = 'hr.leave.accrual.template'
    _description = 'Leave Accrual Template'
    _columns = {
        'name': fields.char(
            'Template Name',
            required=True,
        ),
        'code': fields.char(
            'Template Code',
            required=True,
        ),
        'amount_type': fields.selection(
            get_amount_types,
            string="Amount Type",
        ),
        'line_ids': fields.one2many(
            'hr.leave.accrual.template.line',
            'template_id',
            'Accrual Template Lines',
        ),
    }
