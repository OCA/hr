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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, utc

from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _

import logging
_l = logging.getLogger(__name__)


class restday(osv.TransientModel):

    _name = 'hr.restday.wizard'
    _description = 'Schedule Template Change Wizard'

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'contract_id': fields.related('employee_id', 'contract_id', type='many2one',
                                      relation='hr.contract', string='Contract', readonly=True),
        'st_current_id': fields.many2one('hr.schedule.template', 'Current Template', readonly=True),
        'st_new_id': fields.many2one('hr.schedule.template', 'New Template'),
        'permanent': fields.boolean('Make Permanent'),
        'temp_restday': fields.boolean('Temporary Rest Day Change', help="If selected, change the rest day to the specified day only for the selected schedule."),
        'dayofweek': fields.selection([('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'), ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')], 'Rest Day', select=True),
        'temp_week_start': fields.date('Start of Week'),
        'week_start': fields.date('Start of Week'),
    }

    _defaults = {
        'temp_restday': False,
    }

    def onchange_employee(self, cr, uid, ids, ee_id, context=None):

        res = {'value': {'st_current_id': False}}
        if ee_id:
            ee = self.pool.get('hr.employee').browse(
                cr, uid, ee_id, context=None)
            res['value'][
                'st_current_id'] = ee.contract_id.schedule_template_id.id

        return res

    def onchange_week(self, cr, uid, ids, newdate):

        res = {'value': {'week_start': newdate}}
        if newdate:
            d = datetime.strptime(newdate, "%Y-%m-%d")
            if d.weekday() != 0:
                res['value']['week_start'] = False
                return res
        return res

    def onchange_temp_week(self, cr, uid, ids, newdate):

        res = {'value': {'temp_week_start': newdate}}
        if newdate:
            d = datetime.strptime(newdate, "%Y-%m-%d")
            if d.weekday() != 0:
                res['value']['temp_week_start'] = False
                return res
        return res

    def _create_detail(
        self, cr, uid, schedule, actual_dayofweek, template_dayofweek,
            week_start, context=None):

        # First, see if there's a schedule for the actual dayofweek. If so, use it.
        #
        for worktime in schedule.template_id.worktime_ids:
            if worktime.dayofweek == actual_dayofweek:
                template_dayofweek = actual_dayofweek

        prevutcdtStart = False
        prevDayofWeek = False
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        local_tz = timezone(user.tz)
        dSchedStart = datetime.strptime(schedule.date_start, OE_DFORMAT).date()
        dWeekStart = schedule.date_start < week_start and datetime.strptime(
            week_start, OE_DFORMAT).date() or dSchedStart

        for worktime in schedule.template_id.worktime_ids:

            if worktime.dayofweek != template_dayofweek:
                continue

            hour, sep, minute = worktime.hour_from.partition(':')
            toHour, toSep, toMin = worktime.hour_to.partition(':')
            if len(sep) == 0 or len(toSep) == 0:
                raise osv.except_osv(
                    _('Invalid Time Format'), _('The time should be entered as HH:MM'))

            # XXX - Someone affected by DST should fix this
            #
            dtStart = datetime.strptime(dWeekStart.strftime(
                '%Y-%m-%d') + ' ' + hour + ':' + minute + ':00', '%Y-%m-%d %H:%M:%S')
            locldtStart = local_tz.localize(dtStart, is_dst=False)
            utcdtStart = locldtStart.astimezone(utc)
            if actual_dayofweek != '0':
                utcdtStart = utcdtStart + \
                    relativedelta(days=+int(actual_dayofweek))
            dDay = utcdtStart.astimezone(local_tz).date()

            # If this worktime is a continuation (i.e - after lunch) set the start
            # time based on the difference from the previous record
            #
            if prevDayofWeek and prevDayofWeek == actual_dayofweek:
                prevHour = prevutcdtStart.strftime('%H')
                prevMin = prevutcdtStart.strftime('%M')
                curHour = utcdtStart.strftime('%H')
                curMin = utcdtStart.strftime('%M')
                delta_seconds = (datetime.strptime(curHour + ':' + curMin, '%H:%M')
                                 - datetime.strptime(prevHour + ':' + prevMin, '%H:%M')).seconds
                utcdtStart = prevutcdtStart + \
                    timedelta(seconds=+delta_seconds)
                dDay = prevutcdtStart.astimezone(local_tz).date()

            delta_seconds = (datetime.strptime(toHour + ':' + toMin, '%H:%M')
                             - datetime.strptime(hour + ':' + minute, '%H:%M')).seconds
            utcdtEnd = utcdtStart + timedelta(seconds=+delta_seconds)

            val = {
                'name': schedule.name,
                'dayofweek': actual_dayofweek,
                'day': dDay,
                'date_start': utcdtStart.strftime('%Y-%m-%d %H:%M:%S'),
                'date_end': utcdtEnd.strftime('%Y-%m-%d %H:%M:%S'),
                'schedule_id': schedule.id,
            }
            self.pool.get(
                'hr.schedule').write(cr, uid, schedule.id, {'detail_ids': [(0, 0, val)]},
                                     context=context)

            prevDayofWeek = worktime.dayofweek
            prevutcdtStart = utcdtStart

    def _change_restday(self, cr, uid, employee_id, week_start, dayofweek, context=None):

        sched_obj = self.pool.get('hr.schedule')
        sched_detail_obj = self.pool.get('hr.schedule.detail')

        schedule_ids = sched_obj.search(
            cr, uid, [('employee_id', '=', employee_id),
                      ('date_start', '<=', week_start),
                      ('date_end', '>=', week_start),
                      ('state', 'not in', ['locked'])],
            context=context)
        sched = sched_obj.browse(cr, uid, schedule_ids[0], context=context)
        dtFirstDay = datetime.strptime(
            sched.detail_ids[0].date_start, OE_DTFORMAT)
        date_start = dtFirstDay.strftime(OE_DFORMAT) < week_start and week_start + \
            ' ' + dtFirstDay.strftime(
                '%H:%M:%S') or dtFirstDay.strftime(OE_DTFORMAT)
        dtNextWeek = datetime.strptime(
            date_start, OE_DTFORMAT) + relativedelta(weeks=+1)

        # First get the current rest days
        rest_days = sched_obj.get_rest_days_by_id(
            cr, uid, sched.id, dtFirstDay.strftime(OE_DFORMAT),
            context=context)

        # Next, remove the schedule detail for the new rest day
        for dtl in sched.detail_ids:
            if dtl.date_start < week_start or datetime.strptime(dtl.date_start, OE_DTFORMAT) >= dtNextWeek:
                continue
            if dtl.dayofweek == dayofweek:
                sched_detail_obj.unlink(cr, uid, dtl.id, context=context)

        # Enter the new rest day(s)
        #
        sched_obj = self.pool.get('hr.schedule')
        nrest_days = [dayofweek] + rest_days[1:]
        dSchedStart = datetime.strptime(sched.date_start, OE_DFORMAT).date()
        dWeekStart = sched.date_start < week_start and datetime.strptime(
            week_start, OE_DFORMAT).date() or dSchedStart
        if dWeekStart == dSchedStart:
            sched_obj.add_restdays(
                cr, uid, sched, 'restday_ids1', rest_days=nrest_days, context=context)
        elif dWeekStart == dSchedStart + relativedelta(days=+7):
            sched_obj.add_restdays(
                cr, uid, sched, 'restday_ids2', rest_days=nrest_days, context=context)
        elif dWeekStart == dSchedStart + relativedelta(days=+14):
            sched_obj.add_restdays(
                cr, uid, sched, 'restday_ids3', rest_days=nrest_days, context=context)
        elif dWeekStart == dSchedStart + relativedelta(days=+21):
            sched_obj.add_restdays(
                cr, uid, sched, 'restday_ids4', rest_days=nrest_days, context=context)
        elif dWeekStart == dSchedStart + relativedelta(days=+28):
            sched_obj.add_restdays(
                cr, uid, sched, 'restday_ids5', rest_days=nrest_days, context=context)

        # Last, add a schedule detail for the first rest day in the week using the
        # template for the new (temp) rest day
        #
        if len(rest_days) > 0:
            self._create_detail(
                cr, uid, sched, str(rest_days[0]), dayofweek, week_start,
                context=context)

    def _remove_add_schedule(self, cr, uid, schedule_id, week_start, tpl_id, context=None):

        # Remove the current schedule and add a new one in its place according to
        # the new template. If the week that the change starts in is not at the
        # beginning of a schedule create two new schedules to accomodate the
        # truncated old one and the partial new one.
        #

        sched_obj = self.pool.get('hr.schedule')
        sched = sched_obj.browse(cr, uid, schedule_id, context=context)

        vals2 = False
        vals1 = {
            'name': sched.name,
            'employee_id': sched.employee_id.id,
            'template_id': tpl_id,
            'date_start': sched.date_start,
            'date_end': sched.date_end,
        }

        if week_start > sched.date_start:
            dWeekStart = datetime.strptime(week_start, '%Y-%m-%d').date()
            start_day = dWeekStart.strftime('%Y-%m-%d')
            vals1['template_id'] = sched.template_id.id
            vals1['date_end'] = (
                dWeekStart + relativedelta(days=-1)).strftime('%Y-%m-%d')
            vals2 = {
                'name': sched.employee_id.name + ': ' + start_day + ' Wk ' + str(dWeekStart.isocalendar()[1]),
                'employee_id': sched.employee_id.id,
                'template_id': tpl_id,
                'date_start': start_day,
                'date_end': sched.date_end,
            }

        sched_obj.unlink(cr, uid, schedule_id, context=context)
        _l.warning('vals1: %s', vals1)
        sched_obj.create(cr, uid, vals1, context=context)
        if vals2:
            _l.warning('vals2: %s', vals2)
            sched_obj.create(cr, uid, vals2, context=context)

    def _change_by_template(self, cr, uid, employee_id, week_start, new_template_id, doall, context=None):

        sched_obj = self.pool.get('hr.schedule')

        schedule_ids = sched_obj.search(
            cr, uid, [('employee_id', '=', employee_id),
                      ('date_start', '<=', week_start),
                      ('date_end', '>=', week_start),
                      ('state', 'not in', ['locked'])],
            context=context)

        # Remove the current schedule and add a new one in its place according to
        # the new template
        #
        if len(schedule_ids) > 0:
            self._remove_add_schedule(
                cr, uid, schedule_ids[0], week_start, new_template_id,
                context=context)

        # Also, change all subsequent schedules if so directed
        if doall:
            ids = sched_obj.search(cr, uid, [('employee_id', '=', employee_id),
                                             ('date_start', '>', week_start),
                                             ('state', 'not in', ['locked'])],
                                   context=context)
            for i in ids:
                self._remove_add_schedule(
                    cr, uid, i, week_start, new_template_id, context)

    def change_restday(self, cr, uid, ids, context=None):

        data = self.read(cr, uid, ids[0], [], context=context)

        # Change the rest day for only one schedule
        if data.get('temp_restday', False) and data.get('dayofweek', False) and data.get('temp_week_start', False):
            self._change_restday(
                cr, uid, data['employee_id'][0], data['temp_week_start'],
                data['dayofweek'], context=context)

        # Change entire week's schedule to the chosen schedule template
        if not data.get('temp_restday', False) and data.get('st_new_id', False) and data.get('week_start', False):

            if data.get('week_start', False):
                self._change_by_template(
                    cr, uid, data['employee_id'][0], data['week_start'],
                    data['st_new_id'][0], data.get(
                        'permanent', False),
                    context=context)

            # If this change is permanent modify employee's contract to reflect the new template
            #
            if data.get('permanent', False):
                self.pool.get(
                    'hr.contract').write(cr, uid, data['contract_id'][0],
                                         {'schedule_template_id': data[
                                             'st_new_id'][0]},
                                         context=context)

        return {
            'name': 'Change Schedule Template',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.restday.wizard',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }
