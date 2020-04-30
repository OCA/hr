# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import calendar
from odoo import api, fields, models


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    force_last_month_day = fields.Boolean(
        help='If its used this option, the nextcall will to '
        'take the last day of the month in the date provided.')

    @api.model
    def _update_accrual(self):
        res = super(HolidaysAllocation, self)._update_accrual()

        holidays = self.search([
            ('accrual', '=', True), ('employee_id.active', '=', True),
            ('state', '=', 'validate'), ('holiday_type', '=', 'employee'),
            ('force_last_month_day', '=', True), '|', ('date_to', '=', False),
            ('date_to', '>', fields.Datetime.now()), ('nextcall', '!=', False)])
        for holiday in holidays:
            last_day_of_month = calendar.monthrange(holiday.nextcall.year, holiday.nextcall.month)[1]
            if last_day_of_month == holiday.nextcall.day:
                continue
            holiday.nextcall.replace(day=last_day_of_month)
        return res
