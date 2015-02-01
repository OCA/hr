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


class hr_leave_accrual(orm.Model):
    """
    A leave accrual of an employee
    """
    _name = 'hr.leave.accrual'
    _description = 'Employee Leave Accrual'

    def _get_approved_lines(
        self, cr, uid, ids, context=None
    ):
        """
        Get lines of leave accruals entered mannually plus those
        related to an approved payslip

        return: a dict that contains a list of accrual line objects
        for each accrual id
        """
        result = {}
        if not ids:
            return result

        if isinstance(ids, (int, long)):
            ids = [ids]

        accruals = self.browse(cr, uid, ids, context=context)

        return {
            accrual.id: [
                line for line in accrual.line_ids
                # Lines entered manually or from approved payslip
                if not line.payslip_id or line.state in ['done']
            ]
            for accrual in accruals
        }

    def _sum_lines(
        self, cr, uid, ids, field_names, arg=None, context=None
    ):
        """
        Get the actual total of the leave acruals refered by ids
        """
        approved_lines = self._get_approved_lines(
            cr, uid, ids, context=context
        )

        res = {}

        for accrual_id in approved_lines:
            total_hours = 0
            total_cash = 0
            lines = approved_lines[accrual_id]

            for line in lines:
                if line.is_refund:
                    if line.amount_type == 'cash':
                        total_cash -= line.amount
                    elif line.amount_type == 'hours':
                        total_hours -= line.amount
                else:
                    if line.amount_type == 'cash':
                        total_cash += line.amount
                    elif line.amount_type == 'hours':
                        total_hours += line.amount

            res[accrual_id] = {
                'total_cash': total_cash,
                'total_hours': total_hours,
            }

        return res

    _columns = {
        'leave_type_id': fields.many2one(
            'hr.holidays.status',
            string='Leave Type',
            ondelete='cascade',
        ),
        'code': fields.related(
            'leave_type_id',
            'accrual_code',
            type="char",
        ),
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
            ondelete='cascade',
        ),
        'line_ids': fields.one2many(
            'hr.leave.accrual.line',
            'accrual_id',
            string='Accrual Lines',
        ),
        'total_cash': fields.function(
            _sum_lines,
            method=True,
            type="float",
            string='Hours Accruded',
            multi=True,
        ),
        'total_hours': fields.function(
            _sum_lines,
            method=True,
            type="float",
            multi=True,
            string='Cash Accruded',
        ),
    }
