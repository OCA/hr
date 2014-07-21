#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
from osv import osv, fields


class hr_holidays(osv.osv):

    _name = 'hr.holidays.public'
    _description = 'Public Holidays'

    _columns = {
        'year': fields.char("calendar Year", required=True),
        'line_ids': fields.one2many('hr.holidays.public.line', 'holidays_id', 'Holiday Dates'),
        'country_id': fields.many2one('res.country', 'Country'),
    }

    _rec_name = 'year'
    _order = "year"

    _sql_constraints = [
        ('year_unique', 'UNIQUE(year,country_id)', _('Duplicate year and country!')),
    ]

    def is_public_holiday(self, cr, uid, dt, employee_id=None, context=None):
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        if employee_id == None:
            holidays_filter = [('year', '=', dt.year), ('country_id', '=', False)]
        else:
            if employee.address_id.country_id == None:
                holidays_filter = [('year', '=', dt.year), ('country_id', '=', False)]
            else:
                holidays_filter = [('year', '=', dt.year), '|', ('country_id', '=',
                                          employee.address_id.country_id.id),
                                         ('country_id', '=', False)]

        ph_ids = self.search(cr, uid, holidays_filter,
            context=context)

        if len(ph_ids) == 0:
            return False

        if employee_id == None:
            states_filter = [('holidays_id', 'in',
                                            ph_ids),
                                            ('state_ids', '=', False)]
        else:
            if employee.address_id.state_id == None:
                states_filter = [('holidays_id', 'in',
                                               ph_ids),
                                              ('state_ids', '=', False)]
            else:
                states_filter = [('holidays_id', 'in',
                                                ph_ids),
                                              '|', ('state_ids.id', '=',
                                              employee.address_id.state_id.id),
                                              ('state_ids', '=', False)]

        hr_holiday_public_line_obj = self.pool.get('hr.holidays.public.line')
        holidays_line_ids = hr_holiday_public_line_obj.search(cr, uid,
                                        states_filter)
        for line in hr_holiday_public_line_obj.browse(cr, uid, holidays_line_ids):
            if date.strftime(dt, "%Y-%m-%d") == line.date:
                return True

        return False

    def get_holidays_list(self, cr, uid, year, employee_id=None, context=None):

        res = []
        employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
        if employee_id == None:
            holidays_filter = [('year', '=', year), ('country_id', '=', False)]
        else:
            if employee.address_id.country_id == None:
                holidays_filter = [('year', '=', year), ('country_id', '=', False)]
            else:
                holidays_filter = [('year', '=', year), '|', ('country_id', '=',
                                          employee.address_id.country_id.id),
                                         ('country_id', '=', False)]

        ph_ids = self.search(cr, uid, holidays_filter, context=context)
        if len(ph_ids) == 0:
            return res

        if employee.address_id.state_id == None:
            states_filter = [('holidays_id', 'in',
                                           ph_ids),
                                          ('state_ids', '=', False)]
        else:
            states_filter = [('holidays_id', 'in',
                                            ph_ids),
                                          '|', ('state_ids.id', '=',
                                          employee.address_id.state_id.id),
                                          ('state_ids', '=', False)]

        hr_holiday_public_line_obj = self.pool.get('hr.holidays.public.line')
        holidays_line_ids = hr_holiday_public_line_obj.search(cr, uid,
                                        states_filter)

        [res.append(l.date)
         for l in hr_holiday_public_line_obj.browse(cr, uid, holidays_line_ids, context=context)]
        return res


class hr_holidays_line(osv.osv):

    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date': fields.date('Date', required=True),
        'holidays_id': fields.many2one('hr.holidays.public', 'Holiday Calendar Year'),
        'variable': fields.boolean('Date may change'),
        'state_ids': fields.many2many('res.country.state', 'hr_holiday_public_state_rel', 'line_id', 'state_id', 'Related states')
    }

    _order = "date, name desc"
