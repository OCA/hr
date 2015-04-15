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

from openerp import models, fields, api, _
from datetime import date


class HrPublicHolidays(models.Model):

    _name = 'hr.holidays.public'
    _description = 'Public Holidays'

    year = fields.Char("calendar Year", required=True)
    line_ids = fields.One2many('hr.holidays.public.line', 'holidays_id',
                               'Holiday Dates')
    country_id = fields.Many2one('res.country', 'Country')

    _rec_name = 'year'
    _order = 'year'

    @api.one
    @api.constrains('year')
    def _check_year(self):
        if not self.country_id:
            ids = self.search([('year', '=', self.year),
                               ('country_id', '=', False),
                               ('id', '!=', self.id)])
            if ids:
                raise Warning(_('Error: Duplicate year'))

    _sql_constraints = [
        ('year_unique',
         'UNIQUE(year,country_id)',
         _('Duplicate year and country!')),
    ]

    @api.v7
    def is_public_holiday(self, cr, uid, selected_date, employee_id=None):

        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)

        holidays_filter = [('year', '=', selected_date.year),
                           ('country_id', 'in',
                            list({False, employee.address_id.country_id.id}))]

        ph_objects = self.search(cr, uid, holidays_filter)
        if not ph_objects:
            return False

        states_filter = [('holidays_id.id', 'in', ph_objects)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)]

        hr_holiday_public_line_obj = self.pool.get('hr.holidays.public.line')
        holidays_line_ids = \
            hr_holiday_public_line_obj.search(cr, uid, states_filter)
        holidays_line_objects = \
            hr_holiday_public_line_obj.browse(cr, uid, holidays_line_ids)
        for line in holidays_line_objects:
            if date.strftime(selected_date, "%Y-%m-%d") == line.date:
                return True
        return False

    @api.v8
    def is_public_holiday(self, selected_date, employee_id=None):

        employee = self.env['hr.employee'].browse(employee_id)

        holidays_filter = [('year', '=', selected_date.year),
                           ('country_id', 'in',
                            list({False, employee.address_id.country_id.id}))]

        ph_objects = self.search(holidays_filter)
        if not ph_objects:
            return False

        states_filter = [('holidays_id.id', 'in', ph_objects.ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)]

        hr_holiday_public_line_obj = self.env['hr.holidays.public.line']
        holidays_line_ids = hr_holiday_public_line_obj.search(states_filter)
        for line in holidays_line_ids:
            if date.strftime(selected_date, "%Y-%m-%d") == line.date:
                return True
        return False

    def get_holidays_list(self, year, employee_id=None):

        res = []

        employee = self.env['hr.employee'].browse(employee_id)
        holidays_filter = [('year', '=', year),
                           ('country_id', 'in',
                            list({False, employee.address_id.country_id.id}))]

        ph_objects = self.search(holidays_filter)
        if not ph_objects:
            return res

        states_filter = [('holidays_id.id', 'in', ph_objects.ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter.append(('state_ids', 'in',
                                  list({False,
                                        employee.address_id.state_id.id})))

        res = self.env['hr.holidays.public.line'].search(states_filter)
        return res
