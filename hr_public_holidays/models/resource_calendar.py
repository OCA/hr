# -*- coding: utf-8 -*-
# Copyright 2020 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from datetime import datetime, time
import pytz
from odoo import api, fields, models
from odoo.osv.expression import TRUE_LEAF


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    @api.multi
    def get_leave_intervals(
        self, resource_id=None, start_datetime=None, end_datetime=None,
    ):
        """if our resource is an employee, add public holidays to leaves"""
        result = super(ResourceCalendar, self).get_leave_intervals(
            resource_id=resource_id, start_datetime=start_datetime,
            end_datetime=end_datetime,
        )
        if not resource_id:
            return result
        employee = self.env['hr.employee'].search([
            ('resource_id', '=', resource_id),
        ], limit=1)
        if employee:

            def _add_time_and_convert_utc(_date, _time):
                """Combine a date and time as user wall time and return UTC"""
                time_zone = pytz.timezone(self.env.user.tz or 'UTC')
                result = datetime.combine(
                    fields.Date.from_string(_date), _time,
                )
                result = time_zone.localize(result)
                return result.astimezone(pytz.utc).replace(tzinfo=None)


            holidays = self.env['hr.holidays.public.line'].search([
                start_datetime and ('date', '>=', start_datetime) or TRUE_LEAF,
                end_datetime and ('date', '<=', end_datetime) or TRUE_LEAF,
                '|',
                ('state_ids', '=', False),
                ('state_ids', 'in', employee.address_id.state_id.ids),
                '|',
                ('year_id.country_id', '=', False),
                ('year_id.country_id', '=', employee.address_id.country_id.id),
            ])
            if holidays:
                result.extend(holidays.mapped(
                    lambda x: (
                        _add_time_and_convert_utc(x.date, time(0, 0, 0)),
                        _add_time_and_convert_utc(x.date, time(23, 59, 59)),
                    )
                ))
        return result
