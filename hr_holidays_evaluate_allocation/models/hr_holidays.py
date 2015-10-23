# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

from openerp import models, fields, api


class HrHolidays(models.Model):
    _inherit = 'hr.holidays'

    @api.one
    def check_holidays(self):
        '''
        we are overriding this to ensure that leave requests are evaluated in
        their correct period
        '''
        if (self.holiday_type != 'employee' or self.type != 'remove'
                or not self.employee_id or self.holiday_status_id.limit):
            return
        leave_days = self.holiday_status_id.get_days(
            self.employee_id.id,
            dt=fields.Date.from_string(self.date_from)
        )[self.holiday_status_id.id]
        if (leave_days['remaining_leaves'] < 0
                or leave_days['virtual_remaining_leaves'] < 0):
            # Raising a warning gives a more user-friendly feedback than the
            # default constraint error
            raise Warning('The number of remaining leaves is not sufficient  '
                          'for this leave type.\nPlease verify also the  '
                          'leaves waiting for validation.')
        return True
