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
from openerp.tools.translate import _
from openerp import models, fields, api, _


class hr_holidays(models.Model):

    _name = 'hr.holidays.public'
    _description = 'Public Holidays'

    year = fields.Char("calendar Year", required=True)
    line_ids = fields.One2many('hr.holidays.public.line', 'holidays_id', 'Holiday Dates')
    country_id = fields.Many2one('res.country', 'Country')

    _rec_name = 'year'
    _order = 'year'

    @api.one
    @api.constrains('year')
    def _check_year(self):
        for data in self:
            if not data.country_id:

                ids = self.env['hr.holidays.public'].search([('year', '=', data.year), ('country_id', '=', False),
                                                             ('id', '!=', data.id)])
                if ids:
                    raise Warning(_('Error: Duplicate year'))

    _sql_constraints = [
        ('year_unique',
         'UNIQUE(year,country_id)',
         _('Duplicate year and country!')),
    ]

    def is_public_holiday(self, dt, employee_id=None):
        employee = self.env['hr.employee'].browse(employee_id)

        holidays_filter = [('year', '=', dt.year)]
        if not employee or not employee.address_id.country_id:
            holidays_filter.append(('country_id', '=', False))
        else:
            holidays_filter += ['|', ('country_id', '=',
                                      employee.address_id.country_id.id),
                                ('country_id', '=', False)]

        ph_objects = self.env['hr.holidays.public'].search(holidays_filter)

        ph_ids = list()
        for ph in ph_objects:
            ph_ids.append(ph.id)

        if not ph_ids:
            return False

        states_filter = [('holidays_id.id', 'in', ph_ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)
                              ]

        hr_holiday_public_line_obj = self.env['hr.holidays.public.line']
        holidays_line_ids = hr_holiday_public_line_obj.search(states_filter)
        for line in holidays_line_ids:
            if date.strftime(dt, "%Y-%m-%d") == line.date:
                return True
        return False

    def get_holidays_list(self, year, employee_id=None):

        res = []
        employee = self.env['hr.employee'].browse(employee_id)

        holidays_filter = [('year', '=', year)]
        if not employee or not employee.address_id.country_id:
            holidays_filter.append(('country_id', '=', False))
        else:
            holidays_filter += ['|', ('country_id', '=', employee.address_id.country_id.id), ('country_id', '=', False)]

        ph_objects = self.env['hr.holidays.public'].search(holidays_filter)
        ph_ids = list()
        for ph in ph_objects:
            ph_ids.append(ph.id)

        if not ph_ids:
            return res

        states_filter = [('holidays_id.id', 'in', ph_ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)
                              ]

        res = self.env['hr.holidays.public.line'].search(states_filter)

        return res


class hr_holidays_line(models.Model):

    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'

    name = fields.Char('Name', size=128, required=True, translate=True)
    date = fields.Date('Date', required=True)
    holidays_id = fields.Many2one('hr.holidays.public', 'Holiday Calendar Year')
    variable = fields.Boolean('Date may change')
    state_ids = fields.Many2many('res.country.state', 'hr_holiday_public_state_rel',
                                 'line_id', 'state_id', 'Related states')

    _order = "date, name desc"
