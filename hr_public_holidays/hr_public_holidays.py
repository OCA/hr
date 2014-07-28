# -*- coding:utf-8 -*-
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
from openerp.osv import fields, orm


class hr_holidays(orm.Model):

    _name = 'hr.holidays.public'
    _description = 'Public Holidays'

    _columns = {
        'year': fields.char("calendar Year", required=True),
        'line_ids': fields.one2many('hr.holidays.public.line', 'holidays_id',
                                    'Holiday Dates'),
        'country_id': fields.many2one('res.country', 'Country'),
    }

    _rec_name = 'year'
    _order = "year"

    def _check_year(self, cr, uid, ids, context=None):
        record = self.browse(cr, uid, ids, context=context)
        for data in record:
            if not data.country_id:
                ids = self.search(cr, uid, [('year', '=', data.year),
                                            ('country_id', '=', False),
                                            ('id', '!=', data.id)])
                if ids:
                    return False
        return True

    _constraints = [(_check_year, 'Error: Duplicate year', ['year'])]

    _sql_constraints = [
        ('year_unique',
         'UNIQUE(year,country_id)',
         _('Duplicate year and country!')),
    ]

    def is_public_holiday(self, cr, uid, dt, employee_id=None, context=None):
        employee = self.pool['hr.employee'].browse(cr, uid, employee_id)

        holidays_filter = [('year', '=', dt.year)]
        if not employee or not employee.address_id.country_id:
            holidays_filter.append(('country_id', '=', False))
        else:
            holidays_filter += ['|', ('country_id', '=',
                                      employee.address_id.country_id.id),
                                ('country_id', '=', False)]

        ph_ids = self.search(cr, uid, holidays_filter,
                             context=context)

        if not ph_ids:
            return False

        states_filter = [('holidays_id', 'in', ph_ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)
                              ]

        hr_holiday_public_line_obj = self.pool['hr.holidays.public.line']
        holidays_line_ids = \
            hr_holiday_public_line_obj.search(cr, uid, states_filter)
        lines_obj = \
            hr_holiday_public_line_obj.browse(cr, uid, holidays_line_ids)
        for line in lines_obj:
            if date.strftime(dt, "%Y-%m-%d") == line.date:
                return True

        return False

    def get_holidays_list(self, cr, uid, year, employee_id=None,
                          context=None):

        res = []
        employee = self.pool['hr.employee'].browse(cr, uid, employee_id)

        holidays_filter = [('year', '=', year)]
        if not employee or not employee.address_id.country_id:
            holidays_filter.append(('country_id', '=', False))
        else:
            holidays_filter += ['|', ('country_id', '=',
                                      employee.address_id.country_id.id),
                                ('country_id', '=', False)]

        ph_ids = self.search(cr, uid, holidays_filter, context=context)

        if not ph_ids:
            return res

        states_filter = [('holidays_id', 'in', ph_ids)]
        if not employee or not employee.address_id.state_id:
            states_filter.append(('state_ids', '=', False))
        else:
            states_filter += ['|',
                              ('state_ids', '=', False),
                              ('state_ids.id', '=',
                               employee.address_id.state_id.id)
                              ]

        hr_holiday_public_line_obj = self.pool['hr.holidays.public.line']
        holidays_line_ids = \
            hr_holiday_public_line_obj.search(cr, uid, states_filter)

        [res.append(l.date)
            for l in hr_holiday_public_line_obj.browse(cr,
                                                       uid,
                                                       holidays_line_ids,
                                                       context=context)]
        return res


class hr_holidays_line(orm.Model):

    _name = 'hr.holidays.public.line'
    _description = 'Public Holidays Lines'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date': fields.date('Date', required=True),
        'holidays_id': fields.many2one('hr.holidays.public',
                                       'Holiday Calendar Year'),
        'variable': fields.boolean('Date may change'),
        'state_ids': fields.many2many('res.country.state',
                                      'hr_holiday_public_state_rel',
                                      'line_id', 'state_id', 'Related states')
    }

    _order = "date, name desc"
