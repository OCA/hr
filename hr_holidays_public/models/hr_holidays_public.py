# Copyright 2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import date, datetime, time

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

    leave_type_id = fields.Many2one('hr.leave.type')

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

    @api.multi
    def create_leave_type(self):
        for record in self:
            leave_type = self.env['hr.leave.type'].create({
                'name': _('Public Holidays %s (%s)') % (
                    record.year, record.country_id.name
                ),
                'validity_start': False,
                'allocation_type': 'no',
                'color_name': 'black',
            })
            record.leave_type_id = leave_type.id

    @api.multi
    def generate_public_holidays(self):
        for holidays_calendar in self:
            if not holidays_calendar.leave_type_id:
                holidays_calendar.create_leave_type()
            holidays_calendar.line_ids.generate_leave()


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
        ondelete='cascade',
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

    leave_id = fields.Many2one('hr.leave')

    @api.multi
    def generate_leave(self):
        for record in self:
            leave = self.env['hr.leave'].create({
                'name': "%s %s" % (record.name, record.year_id.year),
                'holiday_status_id': record.year_id.leave_type_id.id,
                'request_date_from': record.date,
                'request_date_to': record.date,
                'date_from': datetime.combine(record.date, time(0, 0, 0, 0)),
                'date_to': datetime.combine(
                    record.date, time(23, 59, 59, 99999)
                ),
                'holiday_type': 'public',
                'employee_id': False,
                'country_id': record.year_id.country_id.id,
                'state_ids': [(6, 0, record.state_ids.ids)]
            })
            leave.action_validate()
            record.leave_id = leave.id

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
