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


class hr_employee(orm.Model):
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    _columns = {
        'leave_accrual_ids': fields.one2many(
            'hr.leave.accrual',
            'employee_id',
            'Leave Accruals',
        ),
    }

    def get_leave_accrual_id(
        self, cr, uid, employee_id, accrual_code=False,
        leave_type_id=False, context=None
    ):
        """
        Get a leave accrual of an employee that matches a leave_code
        :return: the id of a leave accrual
        """
        employee = self.browse(cr, uid, employee_id, context=context)

        accrual_id = False

        for accrual in employee.leave_accrual_ids:
            if accrual_code and accrual.code == accrual_code \
                    or leave_type_id == accrual.leave_type_id.id:
                accrual_id = accrual.id
                break

        # If the employee doesn't have the accrual of the given type,
        # create it
        if not accrual_id:
            if accrual_code:
                leave_type_id = self.pool['hr.holidays.status'].search(
                    cr, uid, [('accrual_code', '=', accrual_code)],
                    context=context)[0]

            accrual_id = self.pool['hr.leave.accrual'].create(
                cr, uid, {
                    'employee_id': employee_id,
                    'leave_type_id': leave_type_id,
                }, context=context)

        return accrual_id
