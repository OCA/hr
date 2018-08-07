# -*- coding: utf-8 -*-

##############################################################################
#
#    Clear Groups for Odoo
#    Copyright (C) 2016 Bytebrand GmbH (<http://www.bytebrand.net>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import fields, models, api, _
from openerp.exceptions import Warning as UserError


class HrPublicHolidaysLine(models.Model):
    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'
    _order = "date, name desc"

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
    variable = fields.Boolean('Date may change')
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
        for r in self:
            r._check_date_state_one()

    def _check_date_state_one(self):
        if fields.Date.from_string(self.date).year != self.year_id.year:
            raise UserError(_(
                'Dates of holidays should be the same year '
                'as the calendar year they are being assigned to'
            ))
        if self.state_ids:
            domain = [('date', '=', self.date),
                      ('year_id', '=', self.year_id.id),
                      ('state_ids', '!=', False),
                      ('id', '!=', self.id)]
            holidays = self.search(domain)
            for holiday in holidays:
                if self.state_ids & holiday.state_ids:
                    raise UserError(_('You can\'t create duplicate public '
                                      'holiday per date %s and one of the '
                                      'country states.') % self.date)
        domain = [('date', '=', self.date),
                  ('year_id', '=', self.year_id.id),
                  ('state_ids', '=', False)]
        if self.search_count(domain) > 1:
            raise UserError(_('You can\'t create duplicate public holiday '
                            'per date %s.') % self.date)
        return True
