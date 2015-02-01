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
from .hr_holidays_status_accrual_line import get_amount_types


class hr_leave_accrual_line(orm.Model):
    """
    There are two types of leave accrual lines for now.
        - Those entered manually
        - Those related to a payslip

    If it is related to a payslip, the payslip needs to be approved
    for the line to be included in the accrual's total.
    """
    _name = 'hr.leave.accrual.line'
    _description = 'Leave Accrual Line'
    _columns = {
        # Mandatory fields
        'accrual_id': fields.many2one(
            'hr.leave.accrual',
            'Leave Accrual',
            ondelete='cascade',
            required=True,
        ),
        'amount': fields.float(
            'Amount',
            required=True,
        ),
        'source': fields.selection(
            [
                ('payslip', 'Payslip Line'),
                ('allocation', 'Allocation'),
                ('manual', 'Entered Manually'),
            ],
            type='char',
            string="Source",
            required=True,
        ),
        'amount_type': fields.selection(
            get_amount_types,
            string="Amount Type",
        ),

        # Fields required when line is an allocation
        'allocation_id': fields.many2one(
            'hr.holidays',
            'Allocation',
            ondelete='cascade',
        ),

        # Fields required when line is related to a payslip line
        'payslip_id': fields.many2one(
            'hr.payslip',
            'Payslip',
            ondelete='cascade',
        ),
        'payslip_line_id': fields.many2one(
            'hr.payslip.line',
            'Payslip Line',
            ondelete='cascade',
        ),
        'state': fields.related(
            'payslip_id',
            'state',
            type="char",
            string="State"
        ),
        'is_refund': fields.boolean(
            'Is Refund',
        ),

        # Fields required when the line is entered manually
        'date': fields.date(
            'Date',
        ),
        'description': fields.char(
            'Description',
        )
    }
    _defaults = {
        'payslip_id': False,
        'payslip_line_id': False,
        'source': 'manual',
        'amount_type': 'cash',
    }
