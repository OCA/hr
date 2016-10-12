# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        elif schedule and self.contract_id and self.contract_id.working_hours:
            hours = self.contract_id.working_hours.get_working_hours_of_date(
                datetime.combine(date_dt, time.min))
            if not hours:
                return False
        elif schedule and (not self.contract_id or (
                self.contract_id and not self.contract_id.working_hours)):
            return date_dt.weekday() not in (5, 6)
        return True
