# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    Copyright (c) 2005-2006 Axelor SARL. (http://www.axelor.com)
#    and 2004-2010 Tiny SPRL (<http://tiny.be>).
#    All Rights Reserved.
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
#

from datetime import datetime, timedelta
from pytz import timezone, utc

from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _


class hr_holidays_status(orm.Model):

    _inherit = 'hr.holidays.status'

    _columns = {
        'ex_rest_days': fields.boolean(
            'Exclude Rest Days',
            help="If enabled, the employee's day off is skipped in leave days "
                 "calculation.",
        ),
        'ex_public_holidays': fields.boolean(
            'Exclude Public Holidays',
            help="If enabled, public holidays are skipped in leave days "
            "calculation.",
        ),
    }


class hr_holidays(orm.Model):

    _name = 'hr.holidays'
    _inherit = ['hr.holidays', 'ir.needaction_mixin']

    _columns = {
        'real_days': fields.float(
            'Total Days',
            digits=(16, 1),
        ),
        'rest_days': fields.float(
            'Rest Days',
            digits=(16, 1),
        ),
        'public_holiday_days': fields.float(
            'Public Holidays',
            digits=(16, 1),
        ),
        'return_date': fields.char(
            'Return Date',
            size=32,
        ),
    }

    def _employee_get(self, cr, uid, context=None):

        if context is None:
            context = {}

        # If the user didn't enter from "My Leaves" don't pre-populate Employee
        # field
        import logging
        _l = logging.getLogger(__name__)
        _l.warning('context: %s', context)
        if not context.get('search_default_my_leaves', False):
            return False

        ids = self.pool.get('hr.employee').search(
            cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False

    def _days_get(self, cr, uid, context=None):

        if context is None:
            context = {}

        date_from = context.get('default_date_from')
        date_to = context.get('default_date_to')
        if date_from and date_to:
            delta = datetime.strptime(date_to, OE_DTFORMAT) - \
                datetime.strptime(date_from, OE_DTFORMAT)
            return delta.days or 1
        return False

    _defaults = {
        'employee_id': _employee_get,
        'number_of_days_temp': _days_get,
    }

    _order = 'date_from asc, type desc'

    def _needaction_domain_get(self, cr, uid, context=None):

        users_obj = self.pool.get('res.users')
        domain = []

        if users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            domain = [('state', 'in', ['draft', 'confirm'])]
            return domain

        elif users_obj.has_group(
                cr, uid, 'hr_holidays_extension.group_hr_leave'):
            domain = [('state', 'in', ['confirm']), (
                'employee_id.user_id', '!=', uid)]
            return domain

        return False

    def onchange_bynumber(
            self, cr, uid, ids, no_days, date_from, employee_id,
            holiday_status_id, context=None):
        """
        Update the dates based on the number of days requested.
        """

        ee_obj = self.pool['hr.employee']
        status_obj = self.pool['hr.holidays.status']
        holiday_obj = self.pool['hr.holidays.public']
        sched_tpl_obj = self.pool['hr.schedule.template']
        sched_detail_obj = self.pool['hr.schedule.detail']
        result = {'value': {}}

        if not no_days or not date_from or not employee_id:
            return result

        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user and user.tz:
            local_tz = timezone(user.tz)
        else:
            local_tz = timezone('Africa/Addis_Ababa')

        dt = datetime.strptime(date_from, OE_DTFORMAT)
        employee = ee_obj.browse(cr, uid, employee_id, context=context)
        if holiday_status_id:
            hs_data = status_obj.read(
                cr, uid, holiday_status_id,
                ['ex_rest_days', 'ex_public_holidays'],
                context=context
            )
        else:
            hs_data = {}
        ex_rd = hs_data.get('ex_rest_days', False)
        ex_ph = hs_data.get('ex_public_holidays', False)

        # Get rest day and the schedule start time on the date the leave begins
        #
        rest_days = []
        times = tuple()
        if (ex_rd and employee.contract_id and
                employee.contract_id.schedule_template_id):
            rest_days = sched_tpl_obj.get_rest_days(
                cr, uid, employee.contract_id.schedule_template_id.id,
                context=context
            )
            times = sched_detail_obj.scheduled_begin_end_times(
                cr, uid, employee.id,
                employee.contract_id.id, dt,
                context=context)
        if len(times) > 0:
            utcdtStart = times[0][0]
        else:
            dtStart = local_tz.localize(
                datetime.strptime(dt.strftime(OE_DFORMAT) + ' 00:00:00',
                                  OE_DTFORMAT),
                is_dst=False
            )
            utcdtStart = dtStart.astimezone(utc)

        count_days = no_days
        real_days = 1
        ph_days = 0
        r_days = 0
        next_dt = dt
        while count_days > 1:
            public_holiday = holiday_obj.is_public_holiday(
                cr, uid, next_dt.date(), employee_id=employee_id,
                context=context)
            public_holiday = (public_holiday and ex_ph)
            rest_day = (next_dt.weekday() in rest_days and ex_rd)
            next_dt += timedelta(days=+1)
            if public_holiday or rest_day:
                if public_holiday:
                    ph_days += 1
                elif rest_day:
                    r_days += 1
                real_days += 1
                continue
            else:
                count_days -= 1
                real_days += 1
        while (
                (next_dt.weekday() in rest_days and ex_rd) or
                (holiday_obj.is_public_holiday(
                    cr, uid, next_dt.date(), context=context) and ex_ph)):
            if holiday_obj.is_public_holiday(
                    cr, uid, next_dt.date(), context=context):
                ph_days += 1
            elif next_dt.weekday() in rest_days:
                r_days += 1
            next_dt += timedelta(days=1)
            real_days += 1

        # Set end time based on schedule
        #
        times = sched_detail_obj.scheduled_begin_end_times(
            cr, uid, employee.id,
            employee.contract_id.id, next_dt,
            context=context)
        if len(times) > 0:
            utcdtEnd = times[-1][1]
        else:
            dtEnd = local_tz.localize(
                datetime.strptime(next_dt.strftime(OE_DFORMAT) + ' 23:59:59',
                                  OE_DTFORMAT), is_dst=False)
            utcdtEnd = dtEnd.astimezone(utc)

        result['value'].update({'department_id': employee.department_id.id,
                                'date_from': utcdtStart.strftime(OE_DTFORMAT),
                                'date_to': utcdtEnd.strftime(OE_DTFORMAT),
                                'rest_days': r_days,
                                'public_holiday_days': ph_days,
                                'real_days': real_days})
        return result

    def onchange_enddate(
            self, cr, uid, ids, employee_id, date_to, holiday_status_id,
            context=None):

        ee_obj = self.pool['hr.employee']
        status_obj = self.pool['hr.holidays.status']
        holiday_obj = self.pool['hr.holidays.public']
        sched_tpl_obj = self.pool['hr.schedule.template']
        res = {'value': {'return_date': False}}

        if not employee_id or not date_to:
            return res

        if holiday_status_id:
            hs_data = status_obj.read(
                cr, uid, holiday_status_id,
                ['ex_rest_days', 'ex_public_holidays'],
                context=context
            )
        else:
            hs_data = {}
        ex_rd = hs_data.get('ex_rest_days', False)
        ex_ph = hs_data.get('ex_public_holidays', False)

        rest_days = []
        if ex_rd:
            ee = ee_obj.browse(cr, uid, employee_id, context=context)
            if ee.contract_id and ee.contract_id.schedule_template_id:
                rest_days = sched_tpl_obj.get_rest_days(
                    cr, uid, ee.contract_id.schedule_template_id.id,
                    context=context
                )

        dt = datetime.strptime(date_to, OE_DTFORMAT)
        return_date = dt + timedelta(days=+1)
        while (
            (return_date.weekday() in rest_days and ex_rd) or
            (holiday_obj.is_public_holiday(
                cr, uid, return_date.date(), context=context) and ex_ph)):
            return_date += timedelta(days=1)
        res['value']['return_date'] = return_date.strftime('%B %d, %Y')
        return res

    def create(self, cr, uid, vals, context=None):

        att_obj = self.pool.get('hr.attendance')
        if (
                vals.get('date_from') and vals.get('date_to') and
                vals.get('type') == 'remove' and
                vals.get('holiday_type') == 'employee'):
            att_ids = att_obj.search(
                cr, uid, [
                    ('employee_id', '=', vals['employee_id']),
                    ('name', '>=', vals['date_from']),
                    ('name', '<=', vals['date_to'])
                ], context=context)
            if len(att_ids) > 0:
                raise orm.except_orm(
                    _('Warning'),
                    _('There is already one or more attendance records for '
                      'the date you have chosen.')
                )
        return super(hr_holidays, self).create(cr, uid, vals, context=context)

    def holidays_first_validate(self, cr, uid, ids, context=None):

        self._check_validate(cr, uid, ids, context=context)
        return super(hr_holidays, self).holidays_first_validate(
            cr, uid, ids, context=context
        )

    def holidays_validate(self, cr, uid, ids, context=None):
        self._check_validate(cr, uid, ids, context=context)
        return super(hr_holidays, self).holidays_validate(
            cr, uid, ids, context=context
        )

    def _check_validate(self, cr, uid, ids, context=None):
        users_obj = self.pool.get('res.users')
        if not users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            for leave in self.browse(cr, uid, ids, context=context):
                if leave.employee_id.user_id.id == uid:
                    raise orm.except_orm(
                        _('Warning!'),
                        _('You cannot approve your own leave:\nHoliday Type: '
                          '%s\nEmployee: %s') % (leave.holiday_status_id.name,
                                                 leave.employee_id.name)
                    )
        return


class hr_attendance(orm.Model):

    _name = 'hr.attendance'
    _inherit = 'hr.attendance'

    def create(self, cr, uid, vals, context=None):

        if vals.get('name', False):
            lv_ids = self.pool.get('hr.holidays').search(
                cr, uid, [
                    ('employee_id', '=', vals['employee_id']),
                    ('type', '=', 'remove'),
                    ('date_from', '<=', vals['name']),
                    ('date_to', '>=', vals['name']),
                    ('state', 'not in', ['cancel', 'refuse'])
                ], context=context)
            if len(lv_ids) > 0:
                ee_data = self.pool.get('hr.employee').read(
                    cr, uid, vals['employee_id'], ['name'], context=context
                )
                raise orm.except_orm(
                    _('Warning'),
                    _("There is already one or more leaves recorded for the "
                      "date you have chosen:\n"
                      "Employee: %s\n"
                      "Date: %s" % (ee_data['name'], vals['name'])))

        return super(hr_attendance, self).create(
            cr, uid, vals, context=context
        )
