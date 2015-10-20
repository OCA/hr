# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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
#

from datetime import date
from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class HrHolidays(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _rec_name = 'year'
    _order = "year"

    year = fields.Integer(
        required=True,
        default=date.today().year
    )
    line_ids = fields.One2many(
        'hr.holidays.public.line',
        'year_id',
        'Holiday Dates'
    )
    country_id = fields.Many2one(
        'res.country',
        'Country'
    )

    _sql_constraints = [
        ('year_unique',
         'UNIQUE(year,country_id)',
         _('Duplicate year and country!')),
    ]

    @api.one
    @api.constrains('year')
    def _check_year(self):
        if self.search_count([('year', '=', self.year),
                              ('country_id', '=', False),
                              ('id', '!=', self.id)]):
            raise ValidationError('You can\'t create duplicate year')
        return True

    @api.model
    def is_public_holiday(self, dt, employee_id=None):
        employee = employee_id and self.env['hr.employee'].browse(
            employee_id) or None

        dt = isinstance(dt, basestring) and fields.Date.from_string(dt) or dt

        holidays_filter = [('year', '=', dt.year)]
        if not employee or not employee.address_id.country_id:
            holidays_filter.append(('country_id', '=', False))
        else:
            holidays_filter += ['|', ('country_id', '=',
                                      employee.address_id.country_id.id),
                                ('country_id', '=', False)]

        public_holidays = self.search(holidays_filter)

        if not public_holidays:
            return False

        dt_str = fields.Date.to_string(dt)
        states_filter = [('year_id', 'in', public_holidays.ids),
                         ('date', '=', dt_str)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += [
                '|',
                ('state_ids', '=', False),
                ('state_ids.id', '=', employee.address_id.state_id.id)
            ]
        if self.env['hr.holidays.public.line'].search_count(states_filter):
            return True

        return False

    @api.model
    def get_holidays_list(self, year, employee_id=None):
        res = []
        employee = employee_id and self.env['hr.employee'].browse(
            employee_id) or None
        holidays_filter = [('year', '=', year)]
        if not employee or not employee.address_id.country_id:
            holidays_filter.append(('country_id', '=', False))
        else:
            holidays_filter += ['|', ('country_id', '=',
                                      employee.address_id.country_id.id),
                                ('country_id', '=', False)]

        public_holidays = self.search(holidays_filter)

        if not public_holidays:
            return res

        states_filter = [('year_id', 'in', public_holidays.ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)
                              ]
        return self.env['hr.holidays.public.line'].search(
            states_filter).mapped('date')
