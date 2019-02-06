# Copyright 2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrHolidaysPublic(models.Model):
    _name = 'hr.holidays.public'
    _description = 'Public Holidays'
    _rec_name = 'year'
    _order = 'year'

    display_name = fields.Char(
        'Name',
        compute='_compute_display_name',
        store=True,
    )
    year = fields.Integer(
        'Calendar Year',
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

    @api.multi
    @api.constrains('year', 'country_id')
    def _check_year(self):
        for line in self:
            line._check_year_one()

    def _check_year_one(self):
        if self.search_count([
                ('year', '=', self.year),
                ('country_id', '=', self.country_id.id),
                ('id', '!=', self.id)]):
            raise ValidationError(_(
                'You can\'t create duplicate public holiday per year and/or'
                ' country'
            ))
        return True

    @api.multi
    @api.depends('year', 'country_id')
    def _compute_display_name(self):
        for line in self:
            if line.country_id:
                line.display_name = '%s (%s)' % (
                    line.year,
                    line.country_id.name
                )
            else:
                line.display_name = line.year

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
                holidays_filter.append('|')
                holidays_filter.append(('country_id', '=', False))
                holidays_filter.append(('country_id',
                                        '=',
                                        employee.address_id.country_id.id))
            else:
                holidays_filter.append(('country_id', '=', False))
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
        :param selected_date: datetime object
        :param employee_id: ID of the employee
        :return: bool
        """
        holidays_lines = self.get_holidays_list(
            selected_date.year, employee_id=employee_id)
        if holidays_lines:
            hol_date = holidays_lines.filtered(
                lambda r: r.date == selected_date
            )
            if hol_date.ids:
                return True
        return False


class HrHolidaysPublicLine(models.Model):
    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'
    _order = 'date, name desc'

    name = fields.Char(
        'Name',
        required=True,
    )
    date = fields.Date(
        'Date',
        required=True
    )
    year_id = fields.Many2one(
        'hr.holidays.public',
        'Calendar Year',
        required=True,
    )
    variable_date = fields.Boolean(
        'Date may change',
        oldname='variable',
        default=True,
    )
    state_ids = fields.Many2many(
        'res.country.state',
        'hr_holiday_public_state_rel',
        'line_id',
        'state_id',
        'Related States'
    )

    @api.multi
    @api.constrains('date', 'state_ids')
    def _check_date_state(self):
        for line in self:
            line._check_date_state_one()

    def _check_date_state_one(self):
        if self.date.year != self.year_id.year:
            raise ValidationError(_(
                'Dates of holidays should be the same year as the calendar'
                ' year they are being assigned to'
            ))

        if self.state_ids:
            domain = [
                ('date', '=', self.date),
                ('year_id', '=', self.year_id.id),
                ('state_ids', '!=', False),
                ('id', '!=', self.id),
            ]
            holidays = self.search(domain)

            for holiday in holidays:

                if self.state_ids & holiday.state_ids:
                    raise ValidationError(_(
                        'You can\'t create duplicate public holiday per date'
                        ' %s and one of the country states.'
                    ) % self.date)
        domain = [('date', '=', self.date),
                  ('year_id', '=', self.year_id.id),
                  ('state_ids', '=', False)]
        if self.search_count(domain) > 1:
            raise ValidationError(_(
                'You can\'t create duplicate public holiday per date %s.'
            ) % self.date)
        return True
