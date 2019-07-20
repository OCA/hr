# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from pytz import timezone, UTC
from datetime import time

from odoo import api, fields, models


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    @api.model
    def _default_get_request_parameters(self, values):
        HrEmployee = self.env['hr.employee'].sudo()
        tz = timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')

        new_values = dict(values)
        now = fields.Datetime.now()
        date_from = values.get('date_from', now)
        date_to = values.get('date_to', now)

        if not date_from.tzinfo:
            date_from = date_from.replace(tzinfo=UTC)
        if not date_to.tzinfo:
            date_to = date_to.replace(tzinfo=UTC)

        local_date_from = date_from.astimezone(tz)
        local_date_to = date_to.astimezone(tz)

        default_time_from = time(7, 0, 0, 0)
        default_time_to = time(19, 0, 0, 0)

        if date_from == date_to:
            # NOTE: Simulate 7am/7pm default from calendar view
            local_date_from = local_date_from.replace(
                hour=default_time_from.hour,
                minute=default_time_from.minute,
                second=default_time_from.second,
                microsecond=default_time_from.microsecond,
            )
            date_from = local_date_from.astimezone(UTC)
            local_date_to = local_date_to.replace(
                hour=default_time_to.hour,
                minute=default_time_to.minute,
                second=default_time_to.second,
                microsecond=default_time_to.microsecond,
            )
            date_to = local_date_to.astimezone(UTC)

        if values.get('holiday_type', 'employee') == 'employee' \
                and local_date_from.time() == default_time_from \
                and local_date_to.time() == default_time_to:
            employee_id = values.get(
                'employee_id',
                self.env.context.get('default_employee_id')
            )
            if employee_id:
                employee = HrEmployee.browse(employee_id)
            else:
                user_id = values.get('user_id', self.env.user.id)
                employee = HrEmployee.search([
                    ('user_id', '=', user_id)
                ], limit=1)
            if employee.resource_calendar_id:
                intervals = employee.resource_calendar_id._work_intervals(
                    local_date_from,
                    local_date_to,
                    employee.resource_id
                )
                if intervals:
                    date_from = next(iter(intervals))[0].astimezone(UTC)
                    date_to = next(reversed(intervals))[1].astimezone(UTC)

        new_values['date_from'] = date_from.replace(tzinfo=None)
        new_values['date_to'] = date_to.replace(tzinfo=None)

        return super()._default_get_request_parameters(new_values)
