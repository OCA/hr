#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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

from pytz import common_timezones
from openerp.osv import fields, osv


class policy_ot(osv.Model):

    _name = 'hr.policy.ot'

    _columns = {
        'name': fields.char('Name', size=128, required=True),
        'date': fields.date('Effective Date', required=True),
        'line_ids': fields.one2many('hr.policy.line.ot', 'policy_id', 'Policy Lines'),
    }

    # Return records with latest date first
    _order = 'date desc'

    def get_codes(self, cr, uid, idx, context=None):

        res = []
        [res.append((line.code, line.name, line.type, line.rate))
         for line in self.browse(cr, uid, idx, context=context).line_ids]
        return res

    def daily_codes(self, cr, uid, idx, context=None):

        res = []
        [res.append((line.code, line.name))
         for line in self.browse(cr, uid, idx, context=context).line_ids if line.type == 'daily']
        return res

    def restday_codes(self, cr, uid, idx, context=None):

        res = []
        [res.append((line.code, line.name))
         for line in self.browse(cr, uid, idx, context=context).line_ids if line.type == 'weekly' and line.active_after_units == 'day']
        return res

    def restday2_codes(self, cr, uid, idx, context=None):

        res = []
        [res.append((line.code, line.name))
         for line in self.browse(cr, uid, idx, context=context).line_ids if line.type == 'restday']
        return res

    def weekly_codes(self, cr, uid, idx, context=None):

        res = []
        [res.append((line.code, line.name))
         for line in self.browse(cr, uid, idx, context=context).line_ids if line.type == 'weekly' and line.active_after_units == 'min']
        return res

    def holiday_codes(self, cr, uid, idx, context=None):

        res = []
        [res.append((line.code, line.name))
         for line in self.browse(cr, uid, idx, context=context).line_ids if line.type == 'holiday']
        return res


class policy_line_ot(osv.Model):

    _name = 'hr.policy.line.ot'

    def _tz_list(self, cr, uid, context=None):

        res = tuple()
        for name in common_timezones:
            res += ((name, name),)
        return res

    _columns = {
        'name': fields.char('Name', size=64, required=True),
        'policy_id': fields.many2one('hr.policy.ot', 'Policy'),
        'type': fields.selection([('daily', 'Daily'),
                                  ('weekly', 'Weekly'),
                                  ('restday', 'Rest Day'),
                                  ('holiday', 'Public Holiday')],
                                 'Type', required=True),
        'weekly_working_days': fields.integer('Weekly Working Days'),
        'active_after': fields.integer('Active After', help="Minutes after which this policy applies"),
        'active_start_time': fields.char('Active Start Time', size=5, help="Time in 24 hour time format"),
        'active_end_time': fields.char('Active End Time', size=5, help="Time in 24 hour time format"),
        'tz': fields.selection(_tz_list, 'Time Zone'),
        'rate': fields.float('Rate', required=True, help='Multiplier of employee wage.'),
        'code': fields.char('Code', required=True, help="Use this code in the salary rules.")
    }


class policy_group(osv.Model):

    _name = 'hr.policy.group'
    _inherit = 'hr.policy.group'

    _columns = {
        'ot_policy_ids': fields.many2many('hr.policy.ot', 'hr_policy_group_ot_rel',
                                          'group_id', 'ot_id', 'Overtime Policy'),
    }
