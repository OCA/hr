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

    def get_leave_accrual(
        self, cr, uid, employee_id, leave_code, context=None
    ):
        """
        Get a leave accrual of an employee that matches a leave_code
        return: a leave accrual browse record
        """
        employee = self.browse(cr, uid, employee_id, context=context)
        leave_accruals = employee.leave_accrual_ids

        for accrual in leave_accruals:
            if accrual.code == leave_code:
                return accrual.id

        return False
