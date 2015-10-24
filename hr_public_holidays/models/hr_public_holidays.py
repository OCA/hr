# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
##############################################################################
from datetime import date
from openerp import fields, models, api
from openerp.exceptions import ValidationError


class HrPublicHolidays(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _rec_name = 'year'
    _order = "year"

    display_name = fields.Char(
        "Name",
        compute="_compute_display_name",
        readonly=True,
        store=True
    )
    year = fields.Integer(
        "Calendar Year",
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
        ('year_country_unique',
         'UNIQUE(year,country_id)',
         'Duplicate year and country!'),
    ]

    @api.one
    @api.constrains('year')
    def _check_year(self):
        if self.search_count([('year', '=', self.year),
                              ('country_id', '=', False),
                              ('id', '!=', self.id)]):
            raise ValidationError('You can\'t create duplicate year')
        return True

    @api.one
    @api.depends('year', 'country_id')
    def _compute_display_name(self):
        if self.country_id:
            self.display_name = '%s (%s)' % (self.year, self.country_id.name)
        else:
            self.display_name = self.year

    @api.multi
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, rec.display_name))
        return result

    @api.model
    @api.returns('hr.holidays.public.line')
    def get_holidays_list(self, year, employee_id=None):
        """
        Returns recordset of hr.holidays.public.line
        for the specified year and employee
        :param year: year as string
        :param employee_id: ID of the employee
        :return: recordset of hr.holidays.public.line
        """
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
            return list()

        states_filter = [('year_id', 'in', pholidays.ids)]
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
        """
        Returns True if selected_date is a public holiday for the employee
        :param selected_date: datetime object or string
        :param employee_id: ID of the employee
        :return: bool
        """
        if isinstance(selected_date, basestring):
            selected_date = fields.Date.from_string(selected_date)
        holidays_lines = self.get_holidays_list(
            selected_date.year, employee_id=employee_id)
        if len(holidays_lines.filtered(
                lambda r: r.date == fields.Date.to_string(selected_date))):
            return True
        return False
