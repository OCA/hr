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

from datetime import datetime, time
from openerp import models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def work_scheduled_on_day(self, date_dt, public_holiday=True,
                              schedule=True):
        ''''
        returns true or false depending on if employee was scheduled to work
        on a particular day. It does this by both checking if it is a public
        holiday and the resource calendar of the contract
        @param date_dt: date for which to check
        @param public_holiday: optional, whether to consider public holidays,
                               default=True
        @param schedule: optional, whether to consider the contract's resource
                         calendar. default=True
        '''
        self.ensure_one()
        if public_holiday and self.env['hr.holidays.public'].is_public_holiday(
                date_dt, employee_id=self.id):
            return False
        elif (schedule and self.contract_id and self.contract_id.working_hours
              and not self.contract_id.working_hours.get_working_hours_of_date(
                  datetime.combine(date_dt, time.min))[0]):
            return False
        elif schedule and (not self.contract_id or (
                self.contract_id and not self.contract_id.working_hours)):
            return date_dt.weekday() not in (5, 6)
        return True
