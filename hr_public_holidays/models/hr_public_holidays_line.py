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

from openerp import models, fields


class HrPublicHolidaysLine(models.Model):
    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'
    _order = "date, name desc"

    name = fields.Char('Name', required=True, translate=True)
    date = fields.Date('Date', required=True)
    holidays_id = fields.Many2one('hr.holidays.public',
                                  'Holiday Calendar Year')
    variable = fields.Boolean('Date may change')
    state_ids = fields.Many2many('res.country.state',
                                 'hr_holiday_public_state_rel',
                                 'line_id', 'state_id', 'Related states')
