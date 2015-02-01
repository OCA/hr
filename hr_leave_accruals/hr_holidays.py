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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from datetime import datetime


class hr_holidays(orm.Model):
    _inherit = 'hr.holidays'

    _columns = {
        'accrual_line_id': fields.one2many(
            'hr.leave.accrual.line',
            'allocation_id',
            string="Leave Accrual Line",
        ),
    }

    def holidays_validate(self, cr, uid, ids, context=None):
        """
        After an allocation of holidays is validated,
        add hours to the related leave accrual of the employee
        """
        res = super(hr_holidays, self).holidays_validate(
            cr, uid, ids, context=context)

        for leave in self.browse(cr, uid, ids, context=context):
            if leave.type == 'add' and leave.holiday_type == 'employee' \
                    and leave.holiday_status_id.increase_accrual_on_allocation:

                employee = leave.employee_id
                leave_type_id = leave.holiday_status_id.id

                accrual_id = self.pool['hr.employee'].get_leave_accrual_id(
                    cr, uid, employee.id, leave_type_id=leave_type_id,
                    context=None)

                number_of_hours = leave.number_of_days_temp * \
                    employee.company_id.holidays_hours_per_day

                for line in leave.accrual_line_id:
                    line.unlink()

                leave.write({
                    'accrual_line_id': [(0, 0, {
                        'source': 'allocation',
                        'amount': number_of_hours,
                        'accrual_id': accrual_id,
                        'date': datetime.now().strftime(
                            DEFAULT_SERVER_DATE_FORMAT),
                        'description': leave.name,
                        'amount_type': 'hours',
                    })]})

        return res

    def holidays_refuse(self, cr, uid, ids, context=None):
        """
        After an allocation of holidays is refused,
        remove the leave accrual line related
        """
        res = super(hr_holidays, self).holidays_refuse(
            cr, uid, ids, context=context)

        for leave in self.browse(cr, uid, ids, context=context):
                for line in leave.accrual_line_id:
                    line.unlink()

        return res
