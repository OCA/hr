# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Codekaki Systems (<http://codekaki.com>).
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
from datetime import datetime
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import calendar
import logging

_logger = logging.getLogger(__name__)

MONTHS = zip(range(1, 13), calendar.month_name[1:])


def monthrange(year=None, month=None):
    today = datetime.today()
    y = year or today.year
    m = month or today.month
    return y, m, calendar.monthrange(y, m)[1]


class hr_duty_roster_shift(osv.Model):
    _description = "Duty Roster Shift"
    _name = 'hr.duty_roster_shift'

    def default_get(self, cr, uid, fields, context=None):
        defs = super(hr_duty_roster_shift, self).default_get(
            cr, uid, fields, context)
        defs['days'] = context.get('days', 0)
        return defs

    def _get_shift_codes(self, cr, uid, context=None):
        context = context or {}
        if 'shift_codes' not in context:
            model = self.pool.get('hr.shift_code')
            ids = model.search(cr, uid, [], order="code", context=context)
            ret = model.read(cr, uid, ids, ['code'], context=context)
            context['shift_codes'] = [(r['code'], r['code']) for r in ret]
        return context['shift_codes']

    _columns = {
        'duty_roster_id': fields.many2one(
            'hr.duty_roster', 'Duty Roster', required=True,
            ondelete="cascade"),
        'employee_id': fields.many2one(
            'hr.employee', 'Employee', required=True),
        'day_1': fields.selection(_get_shift_codes, string='Day 1', size=1),
        'day_2': fields.selection(_get_shift_codes, string='Day 2', size=1),
        'day_3': fields.selection(_get_shift_codes, string='Day 3', size=1),
        'day_4': fields.selection(_get_shift_codes, string='Day 4', size=1),
        'day_5': fields.selection(_get_shift_codes, string='Day 5', size=1),
        'day_6': fields.selection(_get_shift_codes, string='Day 6', size=1),
        'day_7': fields.selection(_get_shift_codes, string='Day 7', size=1),
        'day_8': fields.selection(_get_shift_codes, string='Day 8', size=1),
        'day_9': fields.selection(_get_shift_codes, string='Day 9', size=1),
        'day_10': fields.selection(_get_shift_codes, string='Day 10', size=1),
        'day_11': fields.selection(_get_shift_codes, string='Day 1', size=1),
        'day_12': fields.selection(_get_shift_codes, string='Day 12', size=1),
        'day_13': fields.selection(_get_shift_codes, string='Day 13', size=1),
        'day_14': fields.selection(_get_shift_codes, string='Day 14', size=1),
        'day_15': fields.selection(_get_shift_codes, string='Day 15', size=1),
        'day_16': fields.selection(_get_shift_codes, string='Day 16', size=1),
        'day_17': fields.selection(_get_shift_codes, string='Day 17', size=1),
        'day_18': fields.selection(_get_shift_codes, string='Day 18', size=1),
        'day_19': fields.selection(_get_shift_codes, string='Day 19', size=1),
        'day_20': fields.selection(_get_shift_codes, string='Day 20', size=1),
        'day_21': fields.selection(_get_shift_codes, string='Day 21', size=1),
        'day_22': fields.selection(_get_shift_codes, string='Day 22', size=1),
        'day_23': fields.selection(_get_shift_codes, string='Day 23', size=1),
        'day_24': fields.selection(_get_shift_codes, string='Day 24', size=1),
        'day_25': fields.selection(_get_shift_codes, string='Day 25', size=1),
        'day_26': fields.selection(_get_shift_codes, string='Day 26', size=1),
        'day_27': fields.selection(_get_shift_codes, string='Day 27', size=1),
        'day_28': fields.selection(_get_shift_codes, string='Day 28', size=1),
        'day_29': fields.selection(_get_shift_codes, string='Day 29', size=1),
        'day_30': fields.selection(_get_shift_codes, string='Day 30', size=1),
        'day_31': fields.selection(_get_shift_codes, string='Day 31', size=1),
        'days': fields.related(
            'duty_roster_id', 'days', type='integer', readonly=True),
    }

    _sql_constraints = [
        ('shift_uniq', 'unique(duty_roster_id, employee_id)',
         'Duplicate employee entries detected for this duty roster.')]


class hr_duty_roster(osv.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'hr.duty_roster'
    _description = 'Duty Roster'

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        roster = self.browse(cr, uid, id, context)
        month = roster.month + 1
        year = roster.year
        if month > 12:
            month = 1
            year = roster.year + 1

        default.update({
            'state': 'draft',
            'name': '%s (Copy)' % roster.name,
            'month': month,
            'year': year,
        })
        return super(hr_duty_roster, self).copy(
            cr, uid, id, default=default, context=context)

    def onchange_month_year(self,
                            cr,
                            uid,
                            ids,
                            month,
                            year,
                            shifts,
                            context=None):
        days = calendar.monthrange(year, month)[1]
        for shift in shifts:
            assignment = shift[2]
            for d in range(1, 32):
                col = 'day_%s' % d
                if d > days:
                    assignment[col] = ''

            assignment['days'] = days
            shift[2] = assignment
        return {
            'value': {'days': days, 'shifts': shifts}
        }

    def _get_days(self, cr, uid, ids, field_name, args=None, context=None):
        res = {}
        if ids:
            for row in self.read(
                    cr, uid, ids, ['year', 'month'], context=context):
                mrange = calendar.monthrange(row['year'], row['month'])
                _id = row['id']
                res[_id] = mrange[1]
        return res

    def _needaction_domain_get(self, cr, uid, context=None):
        res = ['&',
               ('state', '=', 'pending'),
               ('department_id.manager_id.user_id', '=', uid)]
        return res

    def _get_date(self, cr, uid, ids, name, args, context=None):
        res = {}
        for row in self.read(cr, uid, ids, ['year', 'month'], context=context):
            row_id = row['id']
            res[row_id] = datetime(
                year=row['year'], month=row['month'], day=1).isoformat()
        return res

    _columns = {
        'name': fields.char('Name', size=60, required=True),
        'month': fields.selection(MONTHS, 'Month', required=True),
        'year': fields.integer('Year', required=True),
        'date': fields.function(_get_date, type="datetime", method=True),
        'days': fields.function(
            _get_days, type="integer", string='Days', method=True),
        'state': fields.selection(
            [('new', 'New'),
             ('draft', 'Draft'),
             ('pending', 'Pending Approval'),
             ('approved', 'Approved'),
             ('rejected', 'Rejected')], string="State"),
        'shifts': fields.one2many(
            'hr.duty_roster_shift', 'duty_roster_id', string="Shifts"),
        'main_department_id': fields.related(
            'department_id',
            'ancestor_id',
            readonly=True,
            type='many2one',
            relation='hr.department',
            string='Main Department'),
        'department_id': fields.many2one(
            'hr.department', 'Department', required=True),
        'remarks': fields.text('Remarks')
    }

    _defaults = {
        'state': lambda self, cr, uid, context: 'new',
        'month': lambda self, cr, uid, context: monthrange()[1],
        'year': lambda self, cr, uid, context: monthrange()[0],
    }

    def action_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'draft'}, context)

    def action_pending(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'pending'}, context)
        self.message_post(cr, uid, ids, body=_('Submitted for approval'),
                          subtype="hr_roster.mt_submitted", context=context)

    def action_approved(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'approved'}, context)
        self.message_post(cr, uid, ids, body=_('Approved'),
                          subtype="hr_roster.mt_approved", context=context)

    def action_rejected(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'rejected'}, context)
        self.message_post(cr, uid, ids, body=_('Rejected'),
                          subtype="hr_roster.mt_rejected", context=context)

    def has_shifts(self, cr, uid, ids, context=None):
        return self.pool.get('hr.duty_roster_shift').search(
            cr, uid, [('duty_roster_id', 'in', ids)], context=context,
            count=True)

    _sql_constraints = [
        ('uniq_duty_roster',
         'unique(department_id, name, year, month)',
         'Duty roster for the same department, month, year and name has already \
         been created.')]


class hr_shift_code(osv.Model):
    _rec_name = 'code'
    _name = 'hr.shift_code'
    _description = 'Shift Code'

    def _time_diff(self, time_in, time_out):
        """Returns the number of minutes if both time in and time out
        are given."""

        duration = 0
        if time_out and time_in:
            time_in, time_out = [
                datetime.strptime(x, DEFAULT_SERVER_DATETIME_FORMAT) for x in (
                    time_in, time_out)]
            duration = (time_out - time_in).seconds / 60
        return int(duration)

    def _get_duration(self, cr, uid, ids, name, args, context=None):
        res = {}
        for row in self.read(cr, uid, ids, ['time_in', 'time_out'],
                             context=context):
            row_id = row['id']
            time_in, time_out = row['time_in'], row['time_out']
            res[row_id] = self._time_diff(time_in, time_out)
        return res

    def onchange_time(self, cr, uid, ids, time_in, time_out, context=None):
        ret = {}
        ret['value'] = {
            'duration': self._time_diff(time_in, time_out)
        }
        return ret

    _columns = {
        'code': fields.char('Code', size=1, required=True),
        'description': fields.char('Description', size=30),
        'time_in': fields.datetime('Time In'),
        'time_out': fields.datetime('Time Out'),
        'break': fields.char('Break', size=8),
        'day_off': fields.boolean('Day Off'),
        'duration': fields.function(_get_duration, string="Duration",
                                    type="integer", method=True),
    }

    _defaults = {
        'break': lambda self, cr, uid, context: '00:30:00',
    }


class hr_department(osv.osv):
    _inherit = 'hr.department'
    _name = _inherit

    def _get_ancestor_id(self, cr, uid, ids, name, args, context=None):
        res = {}
        root_ids = self.search(cr, uid, [('parent_id', '=', False)])
        for _id in ids:
            for root_id in root_ids:
                if self.search(cr, uid, [('id', 'child_of', root_id),
                                         ('id', '=', _id)], count=True):
                    res[_id] = root_id
                    break
        return res

    _columns = {
        'ancestor_id': fields.function(
            _get_ancestor_id,
            type="many2one",
            obj="hr.department",
            string="Main Department",
            method=True),
    }
hr_department()
