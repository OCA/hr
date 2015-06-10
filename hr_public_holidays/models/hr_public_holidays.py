# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from openerp import models, fields, api, _
from datetime import date, datetime
from openerp.exceptions import ValidationError


class HrPublicHolidays(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _rec_name = 'year'
    _order = 'year'

    year = fields.Char("Calendar Year", required=True,
                       help="Enter the year with a numeric value "
                       "e.g. '2015' or '2016'.")
    line_ids = fields.One2many('hr.holidays.public.line', 'holidays_id',
                               'Holiday Dates')
    country_id = fields.Many2one('res.country', 'Country')

    @api.one
    @api.constrains('year', 'country_id')
    def _check_year(self):
        try:
            datetime.strptime(self.year, '%Y')
        except:
            raise ValidationError(
                _("The year %s must be written with a numeric value "
                  "e.g. '2015' or '2016'.") % self.year)
        if not self.country_id:
            pholidays = self.search([
                ('year', '=', self.year),
                ('country_id', '=', False),
                ('id', '!=', self.id)])
            if pholidays:
                raise ValidationError(
                    _('Error: Duplicate year %s') % self.year)

    _sql_constraints = [
        ('year_unique',
         'UNIQUE(year,country_id)',
         _('Duplicate year and country!')),
    ]

    @api.model
    @api.returns('hr.holidays.public.line')
    def get_holidays_list(self, year, employee_id=None):
        '''
        Returns recordset of hr.holidays.public.line
        for the specified year and employee
        :param year: year as string
        :param employee_id: ID of the employee
        :return: recordset of hr.holidays.public.line
        '''
        holidays_filter = [('year', '=', year)]
        employee = False
        if employee_id:
            employee = self.env['hr.employee'].browse(employee_id)
            if employee.address_id and employee.address_id.country_id:
                holidays_filter.append((
                    'country_id',
                    'in',
                    [False, employee.address_id.country_id.id]))

        pholidays = self.search(holidays_filter)
        if not pholidays:
            return False

        states_filter = [('holidays_id', 'in', pholidays.ids)]
        if employee and employee.address_id and employee.address_id.state_id:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids', '=',
                               employee.address_id.state_id.id)]
        else:
            states_filter.append(('state_ids', '=', False))

        hhplo = self.env['hr.holidays.public.line']
        holidays_lines = hhplo.search(states_filter)
        return holidays_lines

    @api.model
    def is_public_holiday(self, selected_date, employee_id=None):
        '''
        Returns True if selected_date is a public holiday for the employee
        :param selected_date: datetime object
        :param employee_id: ID of the employee
        :return: bool
        '''
        holidays_lines = self.get_holidays_list(
            selected_date.year, employee_id=employee_id)
        for line in holidays_lines:
            if date.strftime(selected_date, "%Y-%m-%d") == line.date:
                return True
        return False
