# -*- coding: utf-8 -*-
# ©  2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import date
from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError


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

    @api.multi
    @api.constrains('year', 'country_id')
    def _check_year(self):
        for r in self:
            r._check_year_one()

    def _check_year_one(self):
        if self.country_id:
            domain = [('year', '=', self.year),
                      ('country_id', '=', self.country_id.id),
                      ('id', '!=', self.id)]
        else:
            domain = [('year', '=', self.year),
                      ('country_id', '=', False),
                      ('id', '!=', self.id)]
        if self.search_count(domain):
            raise UserError(_('You can\'t create duplicate public holiday '
                              'per year and/or country'))
        return True

    @api.multi
    @api.depends('year', 'country_id')
    def _compute_display_name(self):
        for r in self:
            if r.country_id:
                r.display_name = '%s (%s)' % (r.year, r.country_id.name)
            else:
                r.display_name = r.year

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
        hhplo = self.env['hr.holidays.public.line']
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
            return hhplo

        states_filter = [('year_id', 'in', pholidays.ids)]
        if employee and employee.address_id and employee.address_id.state_id:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids', '=',
                               employee.address_id.state_id.id)]
        else:
            states_filter.append(('state_ids', '=', False))

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
        if holidays_lines and len(holidays_lines.filtered(
                lambda r: r.date == fields.Date.to_string(selected_date))):
            return True
        return False
