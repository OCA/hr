# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from pytz import timezone, utc
from datetime import datetime, timedelta

import openerp.addons.decimal_precision as dp
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATEFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIMEFORMAT
from openerp.tools.translate import _
from openerp.osv import fields, orm


class last_X_days:

    """Last X Days
    Keeps track of the days an employee worked/didn't work in the last
    X days.
    """

    def __init__(self, days=6):
        self.limit = days
        self.arr = []

    def push(self, worked=False):
        if len(self.arr) == self.limit:
            self.arr.pop(0)
        self.arr.append(worked)
        return [v for v in self.arr]

    def days_worked(self):
        res = 0
        for d in self.arr:
            if d is True:
                res += 1
        return res


class hr_payslip(orm.Model):

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    def _get_policy(self, policy_group, policy_ids, dDay):
        """Return a policy with an effective date before dDay but
        greater than all others
        """

        if not policy_group or not policy_ids:
            return None

        res = None
        for policy in policy_ids:
            dPolicy = datetime.strptime(policy.date, OE_DATEFORMAT).date()
            if dPolicy <= dDay and (
                    res is None or
                    dPolicy > datetime.strptime(
                        res.date, OE_DATEFORMAT).date()):
                res = policy

        return res

    def _get_ot_policy(self, policy_group, dDay):
        """Return an OT policy with an effective date before dDay but
        greater than all others
        """
        return self._get_policy(policy_group, policy_group.ot_policy_ids, dDay)

    def _get_absence_policy(self, policy_group, dDay):
        """Return an Absence policy with an effective date before dDay
        but greater than all others
        """
        return self._get_policy(
            policy_group, policy_group.absence_policy_ids, dDay
        )

    def _get_presence_policy(self, policy_group, dDay):
        """Return a Presence Policy with an effective date before dDay
        but greater than all others
        """
        return self._get_policy(
            policy_group, policy_group.presence_policy_ids, dDay
        )

    def _get_applied_time(
            self, worked_hours, pol_active_after, pol_duration=None):
        """Returns worked time in hours according to pol_active_after
        and pol_duration.
        """
        applied_min = (worked_hours * 60) - pol_active_after
        if applied_min > 0.01:
            applied_min = (pol_duration is not None and applied_min >
                           pol_duration) and pol_duration or applied_min
        else:
            applied_min = 0
        applied_hours = float(applied_min) / 60.0
        return applied_hours

    def _book_holiday_hours(
        self, cr, uid, contract, presence_policy, ot_policy, attendances,
            holiday_obj, dtDay, rest_days, lsd, worked_hours, context=None):

        done = False
        push_lsd = True
        hours = worked_hours

        # Process normal working hours
        for line in presence_policy.line_ids:
            if line.type == 'holiday':
                holiday_hours = self._get_applied_time(
                    worked_hours, line.active_after,
                    line.duration)
                attendances[line.code]['number_of_hours'] += holiday_hours
                attendances[line.code]['number_of_days'] += 1.0
                hours -= holiday_hours
                done = True

        # Process OT hours
        for line in ot_policy.line_ids:
            if line.type == 'holiday':
                ot_hours = self._get_applied_time(
                    worked_hours, line.active_after)
                attendances[line.code]['number_of_hours'] += ot_hours
                attendances[line.code]['number_of_days'] += 1.0
                hours -= ot_hours
                done = True

        if done and (dtDay.weekday() in rest_days or lsd.days_worked == 6):
            # Mark this day as *not* worked so that subsequent days
            # are not treated as over-time.
            lsd.push(False)
            push_lsd = False

        if -0.01 < hours < 0.01:
            hours = 0
        return hours, push_lsd

    def _book_restday_hours(
        self, cr, uid, contract, presence_policy, ot_policy, attendances,
            dtDay, rest_days, lsd, worked_hours, context=None):

        done = False
        push_lsd = True
        hours = worked_hours

        # Process normal working hours
        for line in presence_policy.line_ids:
            if line.type == 'restday' and dtDay.weekday() in rest_days:
                rd_hours = self._get_applied_time(
                    worked_hours, line.active_after, line.duration)
                attendances[line.code]['number_of_hours'] += rd_hours
                attendances[line.code]['number_of_days'] += 1.0
                hours -= rd_hours
                done = True

        # Process OT hours
        for line in ot_policy.line_ids:
            if line.type == 'restday' and dtDay.weekday() in rest_days:
                ot_hours = self._get_applied_time(
                    worked_hours, line.active_after)
                attendances[line.code]['number_of_hours'] += ot_hours
                attendances[line.code]['number_of_days'] += 1.0
                hours -= ot_hours
                done = True

        if done and (dtDay.weekday() in rest_days or lsd.days_worked == 6):
            # Mark this day as *not* worked so that subsequent days
            # are not treated as over-time.
            lsd.push(False)
            push_lsd = False

        if -0.01 < hours < 0.01:
            hours = 0
        return hours, push_lsd

    def _book_weekly_restday_hours(
        self, cr, uid, contract, presence_policy, ot_policy, attendances,
            dtDay, rest_days, lsd, worked_hours, context=None):

        done = False
        push_lsd = True
        hours = worked_hours

        # Process normal working hours
        for line in presence_policy.line_ids:
            if line.type == 'restday':
                if lsd.days_worked() == line.active_after:
                    rd_hours = self._get_applied_time(
                        worked_hours, line.active_after, line.duration)
                    attendances[line.code]['number_of_hours'] += rd_hours
                    attendances[line.code]['number_of_days'] += 1.0
                    hours -= rd_hours
                    done = True

        # Process OT hours
        for line in ot_policy.line_ids:
            if (line.type == 'weekly' and line.weekly_working_days and
                line.weekly_working_days > 0 and
                    lsd.days_worked() == line.weekly_working_days):
                ot_hours = self._get_applied_time(
                    worked_hours, line.active_after)
                attendances[line.code]['number_of_hours'] += ot_hours
                attendances[line.code]['number_of_days'] += 1.0
                hours -= ot_hours
                done = True

        if done and (dtDay.weekday() in rest_days or lsd.days_worked == 6):
            # Mark this day as *not* worked so that subsequent days
            # are not treated as over-time.
            lsd.push(False)
            push_lsd = False

        if -0.01 < hours < 0.01:
            hours = 0
        return hours, push_lsd

    def holidays_list_init(self, cr, uid, dFrom, dTo, context=None):
        holiday_obj = self.pool.get('hr.holidays.public')
        res = holiday_obj.get_holidays_list(
            cr, uid, dFrom.year, context=context)
        if dTo.year != dFrom.year:
            res += holiday_obj.get_holidays_list(
                cr, uid, dTo.year, context=context)
        return res

    def holidays_list_contains(self, d, holidays_list):
        if d.strftime(OE_DATEFORMAT) in holidays_list:
            return True
        return False

    def attendance_dict_init(
            self, cr, uid, contract, dFrom, dTo, context=None):
        att_obj = self.pool.get('hr.attendance')
        res = {}
        att_list = att_obj.punches_list_init(
            cr, uid, contract.employee_id.id, contract.pps_id,
            dFrom, dTo, context=context)
        res.update({'raw_list': att_list})
        d = dFrom
        while d <= dTo:
            res[d.strftime(
                OE_DATEFORMAT)] = att_obj.total_hours_on_day(
                    cr, uid, contract, d,
                    punches_list=att_list,
                    context=context)
            d += timedelta(days=+1)

        return res

    def attendance_dict_hours_on_day(self, d, attendance_dict):
        return attendance_dict[d.strftime(OE_DATEFORMAT)]

    def attendance_dict_list(self, att_dict):
        return att_dict['raw_list']

    def leaves_list_init(
            self, cr, uid, employee_id, dFrom, dTo, tz, context=None):
        """Returns a list of tuples containing start, end dates for
        leaves within the specified period.
        """
        leave_obj = self.pool.get('hr.holidays')
        dtS = datetime.strptime(
            dFrom.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        dtE = datetime.strptime(
            dTo.strftime(OE_DATEFORMAT) + ' 23:59:59', OE_DATETIMEFORMAT)
        utcdt_dayS = timezone(tz).localize(dtS).astimezone(utc)
        utcdt_dayE = timezone(tz).localize(dtE).astimezone(utc)
        utc_dayS = utcdt_dayS.strftime(OE_DATETIMEFORMAT)
        utc_dayE = utcdt_dayE.strftime(OE_DATETIMEFORMAT)

        leave_ids = leave_obj.search(
            cr, uid, [('state', 'in', ['validate', 'validate1']),
                      ('employee_id', '=', employee_id),
                      ('type', '=', 'remove'),
                      ('date_from', '<=', utc_dayE),
                      ('date_to', '>=', utc_dayS)],
            context=context)
        res = []
        if len(leave_ids) == 0:
            return res

        for leave in leave_obj.browse(cr, uid, leave_ids, context=context):
            res.append({
                'code': leave.holiday_status_id.code,
                'tz': tz,
                'start': utc.localize(datetime.strptime(leave.date_from,
                                                        OE_DATETIMEFORMAT)),
                'end': utc.localize(datetime.strptime(leave.date_to,
                                                      OE_DATETIMEFORMAT))
            })

        return res

    def leaves_list_get_hours(
            self, cr, uid, employee_id, contract_id, sched_tpl_id, d,
            leaves_list, context=None):
        """Return the number of hours of leave on a given date, d."""
        detail_pool = self.pool['hr.schedule.detail']
        code = False
        hours = 0
        if len(leaves_list) == 0:
            return code, hours

        dtS = datetime.strptime(
            d.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        dtE = datetime.strptime(
            d.strftime(OE_DATEFORMAT) + ' 23:59:59', OE_DATETIMEFORMAT)
        for l in leaves_list:
            utcBegin = l['start']
            utcEnd = l['end']
            dtLvBegin = datetime.strptime(
                utcBegin.strftime(OE_DATETIMEFORMAT), OE_DATETIMEFORMAT)
            dtLvEnd = datetime.strptime(
                utcEnd.strftime(OE_DATETIMEFORMAT), OE_DATETIMEFORMAT)
            utcdt_dayS = timezone(l['tz']).localize(dtS).astimezone(utc)
            utcdt_dayE = timezone(l['tz']).localize(dtE).astimezone(utc)
            if utcdt_dayS <= utcEnd and utcdt_dayE >= utcBegin:
                code = l['code']
                sched_tpl_obj = self.pool.get('hr.schedule.template')
                if utcBegin.date() < utcdt_dayS.date() < utcEnd.date():
                    hours = 24
                elif utcBegin.date() == utcdt_dayE.date():
                    hours = float((utcdt_dayE - utcBegin).seconds / 60) / 60.0
                elif utcBegin.date() == utcdt_dayS.date():
                    shift_times = detail_pool.scheduled_begin_end_times(
                        cr, uid, employee_id, contract_id, dtS, context=context
                    )
                    if len(shift_times) > 0:
                        for dtStart, dtEnd in shift_times:
                            if dtLvBegin < dtEnd:
                                dt = (
                                    (dtLvBegin < dtStart) and dtStart or
                                    dtLvBegin)
                                hours += float(
                                    (dtEnd - dt).seconds / 60) / 60.0
                                dtLvBegin = dtEnd
                    else:
                        hours = sched_tpl_obj.get_hours_by_weekday(
                            cr, uid, sched_tpl_id, d.weekday(),
                            context=context) or 8
                else:  # dtTo.date() == dToday
                    shift_times = detail_pool.scheduled_begin_end_times(
                        cr, uid, employee_id, contract_id, dtS, context=context
                    )
                    if len(shift_times) > 0:
                        for dtStart, dtEnd in shift_times:
                            if dtLvEnd > dtStart:
                                dt = (dtLvEnd > dtEnd) and dtEnd or dtLvEnd
                                hours += float(
                                    (dt - dtStart).seconds / 60) / 60.0
                    else:
                        hours = sched_tpl_obj.get_hours_by_weekday(
                            cr, uid, sched_tpl_id, d.weekday(),
                            context=context) or 8

        return code, hours

    # Copied from addons/hr_payroll so that we can override worked days
    # calculation to handle Overtime and absence
    #
    def get_worked_day_lines(
            self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be
                 applied for the given contract between date_from and date_to
        """

        sched_tpl_obj = self.pool.get('hr.schedule.template')
        sched_obj = self.pool.get('hr.schedule')
        detail_obj = self.pool.get('hr.schedule.detail')
        ot_obj = self.pool.get('hr.policy.ot')
        presence_obj = self.pool.get('hr.policy.presence')
        absence_obj = self.pool.get('hr.policy.absence')
        holiday_obj = self.pool.get('hr.holidays.public')

        day_from = datetime.strptime(date_from, "%Y-%m-%d").date()
        day_to = datetime.strptime(date_to, "%Y-%m-%d").date()
        nb_of_days = (day_to - day_from).days + 1

        # Initialize list of public holidays. We only need to calculate it once
        # during the lifetime of this object so attach it directly to it.
        #
        try:
            public_holidays_list = self._mtm_public_holidays_list
        except AttributeError:
            self._mtm_public_holidays_list = self.holidays_list_init(
                cr, uid, day_from, day_to,
                context=context)
            public_holidays_list = self._mtm_public_holidays_list

        def get_ot_policies(policy_group_id, day, data):

            if data is None or not data['_reuse']:
                data = {
                    'policy': None,
                    'daily': None,
                    'restday2': None,
                    'restday': None,
                    'weekly': None,
                    'holiday': None,
                    '_reuse': False,
                }
            elif data['_reuse']:
                return data

            ot_policy = self._get_ot_policy(policy_group_id, day)
            daily_ot = ot_policy and len(
                ot_obj.daily_codes(cr, uid, ot_policy.id, context=context)
            ) > 0 or None
            restday2_ot = ot_policy and len(ot_obj.restday2_codes(
                cr, uid, ot_policy.id, context=context)) > 0 or None
            restday_ot = ot_policy and len(ot_obj.restday_codes(
                cr, uid, ot_policy.id, context=context)) > 0 or None
            weekly_ot = ot_policy and len(
                ot_obj.weekly_codes(cr, uid, ot_policy.id, context=context)
            ) > 0 or None
            holiday_ot = ot_policy and len(ot_obj.holiday_codes(
                cr, uid, ot_policy.id, context=context)) > 0 or None

            data['policy'] = ot_policy
            data['daily'] = daily_ot
            data['restday2'] = restday2_ot
            data['restday'] = restday_ot
            data['weekly'] = weekly_ot
            data['holiday'] = holiday_ot
            return data

        def get_absence_policies(policy_group_id, day, data):

            if data is None or not data.get('_reuse'):
                data = {
                    'policy': None,
                    '_reuse': False,
                }
            elif data['_reuse']:
                return data

            absence_policy = self._get_absence_policy(policy_group_id, day)

            data['policy'] = absence_policy
            return data

        def get_presence_policies(policy_group_id, day, data):

            if data is None or not data.get('_reuse'):
                data = {
                    'policy': None,
                    '_reuse': False,
                }
            elif data['_reuse']:
                return data

            policy = self._get_presence_policy(policy_group_id, day)

            data['policy'] = policy
            return data

        res = []
        for contract in self.pool.get('hr.contract').browse(
                cr, uid, contract_ids, context=context):

            wh_in_week = 0

            # Initialize list of leaves taken by the employee during the month
            leaves_list = self.leaves_list_init(
                cr, uid, contract.employee_id.id,
                day_from, day_to, contract.pps_id.tz, context=context)

            # Get default set of rest days for this employee/contract
            contract_rest_days = sched_tpl_obj.get_rest_days(
                cr, uid, contract.schedule_template_id.id, context=context
            )

            # Initialize dictionary of dates in this payslip and the hours the
            # employee was scheduled to work on each
            sched_hours_dict = detail_obj.scheduled_begin_end_times_range(
                cr, uid,
                contract.employee_id.id,
                contract.id,
                day_from, day_to,
                context=context)

            # Initialize dictionary of hours worked per day
            working_hours_dict = self.attendance_dict_init(
                cr, uid, contract, day_from, day_to,
                context=None)

            # Short-circuit:
            # If the policy for the first day is the same as the one for the
            # last day assume that it will also be the same for the days in
            # between, and reuse the same policy instead of checking for every
            # day.
            #
            ot_data = None
            data2 = None
            ot_data = get_ot_policies(
                contract.policy_group_id, day_from, ot_data)
            data2 = get_ot_policies(contract.policy_group_id, day_to, data2)
            if (
                (ot_data['policy'] and data2['policy']) and
                ot_data['policy'].id == data2['policy'].id
            ):
                ot_data['_reuse'] = True

            absence_data = None
            data2 = None
            absence_data = get_absence_policies(
                contract.policy_group_id, day_from, absence_data)
            data2 = get_absence_policies(
                contract.policy_group_id, day_to, data2)
            if (
                absence_data['policy'] and data2['policy'] and
                absence_data['policy'].id == data2['policy'].id
            ):
                absence_data['_reuse'] = True

            presence_data = None
            data2 = None
            presence_data = get_presence_policies(
                contract.policy_group_id, day_from, presence_data)
            data2 = get_presence_policies(
                contract.policy_group_id, day_to, data2)
            if (
                presence_data['policy'] and data2['policy'] and
                presence_data['policy'].id == data2['policy'].id
            ):
                presence_data['_reuse'] = True

            # Calculate the number of days worked in the last week of
            # the previous month. Necessary to calculate Weekly Rest Day OT.
            #
            lsd = last_X_days()
            att_obj = self.pool.get('hr.attendance')
            att_ids = []
            if len(lsd.arr) == 0:
                d = day_from - timedelta(days=6)
                while d < day_from:
                    att_ids = att_obj.search(cr, uid, [
                        ('employee_id', '=', contract.employee_id.id),
                        ('day', '=', d.strftime(
                            '%Y-%m-%d')),
                    ],
                        order='name',
                        # XXX - necessary to keep
                        # order: in,out,in,out,...
                        context=context)
                    if len(att_ids) > 1:
                        lsd.push(True)
                    else:
                        lsd.push(False)
                    d += timedelta(days=1)

            attendances = {
                'MAX': {
                    'name': _("Maximum Possible Working Hours"),
                    'sequence': 1,
                    'code': 'MAX',
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'contract_id': contract.id,
                },
            }
            leaves = {}
            att_obj = self.pool.get('hr.attendance')
            awol_code = False
            import logging
            _l = logging.getLogger(__name__)
            for day in range(0, nb_of_days):
                dtDateTime = datetime.strptime(
                    (day_from + timedelta(days=day)).strftime('%Y-%m-%d'),
                    '%Y-%m-%d'
                )
                rest_days = contract_rest_days
                normal_working_hours = 0

                # Get Presence data
                #
                presence_data = get_presence_policies(
                    contract.policy_group_id, dtDateTime.date(), presence_data)
                presence_policy = presence_data['policy']
                presence_codes = presence_policy and presence_obj.get_codes(
                    cr, uid, presence_policy.id, context=context) or []
                presence_sequence = 2

                for pcode, pname, ptype, prate, pduration in presence_codes:
                    if attendances.get(pcode, False):
                        continue
                    if ptype == 'normal':
                        normal_working_hours += float(pduration) / 60.0
                    attendances[pcode] = {
                        'name': pname,
                        'code': pcode,
                        'sequence': presence_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': prate,
                        'contract_id': contract.id,
                    }
                    presence_sequence += 1

                # Get OT data
                #
                ot_data = get_ot_policies(
                    contract.policy_group_id, dtDateTime.date(), ot_data)
                ot_policy = ot_data['policy']
                daily_ot = ot_data['daily']
                restday2_ot = ot_data['restday2']
                restday_ot = ot_data['restday']
                weekly_ot = ot_data['weekly']
                ot_codes = ot_policy and ot_obj.get_codes(
                    cr, uid, ot_policy.id, context=context) or []
                ot_sequence = 3

                for otcode, otname, ottype, otrate in ot_codes:
                    if attendances.get(otcode, False):
                        continue
                    attendances[otcode] = {
                        'name': otname,
                        'code': otcode,
                        'sequence': ot_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': otrate,
                        'contract_id': contract.id,
                    }
                    ot_sequence += 1

                # Get Absence data
                #
                absence_data = get_absence_policies(
                    contract.policy_group_id, dtDateTime.date(), absence_data)
                absence_policy = absence_data['policy']
                absence_codes = absence_policy and absence_obj.get_codes(
                    cr, uid, absence_policy.id, context=context) or []
                absence_sequence = 50

                for abcode, abname, abtype, abrate, use_awol in absence_codes:
                    if leaves.get(abcode, False):
                        continue
                    if use_awol:
                        awol_code = abcode
                    if abtype == 'unpaid':
                        abrate = 0
                    elif abtype == 'dock':
                        abrate = -abrate
                    leaves[abcode] = {
                        'name': abname,
                        'code': abcode,
                        'sequence': absence_sequence,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'rate': abrate,
                        'contract_id': contract.id,
                    }
                    absence_sequence += 1

                # For Leave related computations:
                #    actual_rest_days: days that are rest days in schedule that
                #                      was actualy used
                #    scheduled_hours: nominal number of full-time hours for the
                #                     working day. If the employee is scheduled
                #                     for this day we use those hours. If not
                #                     we try to determine the hours he/she
                #                     would have worked based on the schedule
                #                     template attached to the contract.
                #
                actual_rest_days = sched_obj.get_rest_days(
                    cr, uid, contract.employee_id.id,
                    dtDateTime, context=context)
                scheduled_hours = detail_obj.scheduled_hours_on_day_from_range(
                    dtDateTime.date(),
                    sched_hours_dict)

                # If the calculated rest days and actual rest days differ, use
                # actual rest days
                if actual_rest_days is None:
                    pass
                elif len(rest_days) != len(actual_rest_days):
                    rest_days = actual_rest_days
                else:
                    for d in actual_rest_days:
                        if d not in rest_days:
                            rest_days = actual_rest_days
                            break

                if (
                        scheduled_hours == 0 and
                        dtDateTime.weekday() not in rest_days):
                    scheduled_hours = sched_tpl_obj.get_hours_by_weekday(
                        cr, uid, contract.schedule_template_id.id,
                        dtDateTime.weekday(
                        ),
                        context=context)

                # Actual number of hours worked on the day. Based on attendance
                # records.
                wh_on_day = self.attendance_dict_hours_on_day(
                    dtDateTime.date(), working_hours_dict)

                # Is today a holiday?
                public_holiday = self.holidays_list_contains(
                    dtDateTime.date(), public_holidays_list)

                # Keep count of the number of hours worked during the week for
                # weekly OT
                if dtDateTime.weekday() == contract.pps_id.ot_week_startday:
                    wh_in_week = wh_on_day
                else:
                    wh_in_week += wh_on_day

                push_lsd = True
                if wh_on_day:
                    done = False

                    if public_holiday:
                        _hours, push_lsd = self._book_holiday_hours(
                            cr, uid, contract, presence_policy, ot_policy,
                            attendances, holiday_obj, dtDateTime, rest_days,
                            lsd, wh_on_day, context=context
                        )
                        if _hours == 0:
                            done = True
                        else:
                            wh_on_day = _hours

                    if not done and restday2_ot:
                        _hours, push_lsd = self._book_restday_hours(
                            cr, uid, contract, presence_policy, ot_policy,
                            attendances, dtDateTime, rest_days, lsd,
                            wh_on_day, context=context)
                        if _hours == 0:
                            done = True
                        else:
                            wh_on_day = _hours

                    if not done and restday_ot:
                        _hours, push_lsd = self._book_weekly_restday_hours(
                            cr, uid, contract, presence_policy, ot_policy,
                            attendances, dtDateTime, rest_days, lsd,
                            wh_on_day, context=context)
                        if _hours == 0:
                            done = True
                        else:
                            wh_on_day = _hours

                    if not done and weekly_ot:
                        for line in ot_policy.line_ids:
                            if line.type == 'weekly' and (
                                    not line.weekly_working_days or
                                    line.weekly_working_days == 0):
                                _active_after = float(line.active_after) / 60.0
                                if wh_in_week > _active_after:
                                    if wh_in_week - _active_after > wh_on_day:
                                        attendances[line.code][
                                            'number_of_hours'
                                        ] += wh_on_day
                                    else:
                                        attendances[line.code][
                                            'number_of_hours'
                                        ] += wh_in_week - _active_after
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    done = True

                    if not done and daily_ot:

                        # Do the OT between specified times (partial OT) first,
                        # so that it doesn't get double-counted in the regular
                        # OT.
                        #
                        partial_hr = 0
                        hours_after_ot = wh_on_day
                        for line in ot_policy.line_ids:
                            active_after_hrs = float(line.active_after) / 60.0
                            if (
                                line.type == 'daily' and
                                wh_on_day > active_after_hrs and
                                line.active_start_time
                            ):
                                partial_hr = att_obj.partial_hours_on_day(
                                    cr, uid, contract,
                                    dtDateTime, active_after_hrs,
                                    line.active_start_time,
                                    line.active_end_time,
                                    line.tz,
                                    punches_list=self.attendance_dict_list(
                                        working_hours_dict),
                                    context=context)
                                if partial_hr > 0:
                                    attendances[line.code][
                                        'number_of_hours'] += partial_hr
                                    attendances[line.code][
                                        'number_of_days'] += 1.0
                                    hours_after_ot -= partial_hr

                        for line in ot_policy.line_ids:
                            active_after_hrs = float(line.active_after) / 60.0
                            if (
                                line.type == 'daily' and
                                hours_after_ot > active_after_hrs and not
                                line.active_start_time
                            ):
                                attendances[line.code][
                                    'number_of_hours'
                                ] += hours_after_ot - (float(line.active_after)
                                                       / 60.0)
                                attendances[line.code]['number_of_days'] += 1.0

                    if not done:
                        for line in presence_policy.line_ids:
                            if line.type == 'normal':
                                normal_hours = self._get_applied_time(
                                    wh_on_day,
                                    line.active_after,
                                    line.duration)
                                attendances[line.code][
                                    'number_of_hours'] += normal_hours
                                attendances[line.code]['number_of_days'] += 1.0
                                done = True
                                _l.warning('nh: %s', normal_hours)
                                _l.warning('att: %s', attendances[line.code])

                    if push_lsd:
                        lsd.push(True)
                else:
                    lsd.push(False)

                leave_type, leave_hours = self.leaves_list_get_hours(
                    cr, uid, contract.employee_id.id,
                    contract.id, contract.schedule_template_id.id,
                    day_from +
                    timedelta(
                        days=day),
                    leaves_list, context=context)
                if (
                    leave_type and (
                        wh_on_day or scheduled_hours > 0 or
                        dtDateTime.weekday() not in rest_days)
                ):
                    if leave_type in leaves:
                        leaves[leave_type]['number_of_days'] += 1.0
                        leaves[leave_type]['number_of_hours'] += (
                            leave_hours > scheduled_hours
                        ) and scheduled_hours or leave_hours
                    else:
                        leaves[leave_type] = {
                            'name': leave_type,
                            'sequence': 8,
                            'code': leave_type,
                            'number_of_days': 1.0,
                            'number_of_hours': (
                                (leave_hours > scheduled_hours) and
                                scheduled_hours or leave_hours
                            ),
                            'contract_id': contract.id,
                        }
                elif (
                    awol_code and (
                        scheduled_hours > 0 and wh_on_day < scheduled_hours
                    ) and not public_holiday
                ):
                    hours_diff = scheduled_hours - wh_on_day
                    leaves[awol_code]['number_of_days'] += 1.0
                    leaves[awol_code]['number_of_hours'] += hours_diff

                # Calculate total possible working hours in the month
                if dtDateTime.weekday() not in rest_days:
                    attendances['MAX'][
                        'number_of_hours'] += normal_working_hours
                    attendances['MAX']['number_of_days'] += 1

            leaves = [value for key, value in leaves.items()]
            attendances = [value for key, value in attendances.items()]
            res += attendances + leaves
        return res

    def _partial_period_factor(self, payslip, contract):

        dpsFrom = datetime.strptime(payslip.date_from, OE_DATEFORMAT).date()
        dpsTo = datetime.strptime(payslip.date_to, OE_DATEFORMAT).date()
        dcStart = datetime.strptime(contract.date_start, OE_DATEFORMAT).date()
        dcEnd = False
        if contract.date_end:
            dcEnd = datetime.strptime(contract.date_end, OE_DATEFORMAT).date()

        # both start and end of contract are out of the bounds of the payslip
        if dcStart <= dpsFrom and (not dcEnd or dcEnd >= dpsTo):
            return 1

        # One or both start and end of contract are within the bounds of the
        #  payslip
        #
        no_contract_days = 0
        if dcStart > dpsFrom:
            no_contract_days += (dcStart - dpsFrom).days
        if dcEnd and dcEnd < dpsTo:
            no_contract_days += (dpsTo - dcEnd).days

        total_days = (dpsTo - dpsFrom).days + 1
        contract_days = total_days - no_contract_days
        return float(contract_days) / float(total_days)

    def get_utilities_dict(self, cr, uid, contract, payslip, context=None):

        res = {}
        if not contract or not payslip:
            return res

        # Calculate percentage of pay period in which contract lies
        res['PPF'] = {
            'amount': self._partial_period_factor(payslip, contract),
        }

        # Calculate net amount of previous payslip
        imd_obj = self.pool.get('ir.model.data')
        ps_obj = self.pool.get('hr.payslip')
        ps_ids = ps_obj.search(
            cr, uid, [('employee_id', '=', contract.employee_id.id)],
            order='date_from', context=context)
        res.update({'PREVPS': {'exists': 0,
                               'net': 0}
                    })
        if ps_ids > 0:
            # Get database ID of Net salary category
            res_model, net_id = imd_obj.get_object_reference(
                cr, uid, 'hr_payroll', 'NET')

            ps = ps_obj.browse(cr, uid, ps_ids[-1], context=context)
            res['PREVPS']['exists'] = 1
            total = 0
            for line in ps.line_ids:
                if line.salary_rule_id.category_id.id == net_id:
                    total += line.total
            res['PREVPS']['net'] = total

        return res

    # XXX
    # Copied (almost) verbatim from hr_payroll for the sole purpose of adding
    # the 'utils' object to localdict.
    #
    def get_payslip_lines(self, cr, uid, contract_ids, payslip_id, context):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(
                    localdict, category.parent_id, amount)
            if category.code in localdict['categories'].dict:
                localdict['categories'].dict[category.code] = localdict[
                    'categories'].dict[category.code] + amount
            else:
                localdict['categories'].dict[category.code] = amount
            return localdict

        class BrowsableObject(object):

            def __init__(self, pool, cr, uid, employee_id, dict):
                self.pool = pool
                self.cr = cr
                self.uid = uid
                self.employee_id = employee_id
                self.dict = dict

            def __getattr__(self, attr):
                return attr in self.dict and self.dict.__getitem__(attr) or 0.0

        class InputLine(BrowsableObject):

            """a class that will be used into the python code, mainly
            for usability purposes
            """

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("""\
SELECT sum(amount) as sum
FROM hr_payslip as hp, hr_payslip_input as pi
WHERE hp.employee_id = %s
  AND hp.state = 'done'
  AND hp.date_from >= %s
  AND hp.date_to <= %s
  AND hp.id = pi.payslip_id
  AND pi.code = %s""", (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()[0]
                return res or 0.0

        class WorkedDays(BrowsableObject):

            """a class that will be used into the python code, mainly
            for usability purposes
            """

            def _sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("""\
SELECT sum(number_of_days) as number_of_days,
       sum(number_of_hours) as number_of_hours
FROM hr_payslip as hp, hr_payslip_worked_days as pi
WHERE hp.employee_id = %s
  AND hp.state = 'done'
  AND hp.date_from >= %s
  AND hp.date_to <= %s
  AND hp.id = pi.payslip_id
  AND pi.code = %s""", (self.employee_id, from_date, to_date, code))
                return self.cr.fetchone()

            def sum(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[0] or 0.0

            def sum_hours(self, code, from_date, to_date=None):
                res = self._sum(code, from_date, to_date)
                return res and res[1] or 0.0

        class Payslips(BrowsableObject):

            """a class that will be used into the python code, mainly
            for usability purposes
            """

            def sum(self, code, from_date, to_date=None):
                if to_date is None:
                    to_date = datetime.now().strftime('%Y-%m-%d')
                self.cr.execute("""\
SELECT sum(
    case when hp.credit_note = False then (pl.total) else (-pl.total) end
)
FROM hr_payslip as hp, hr_payslip_line as pl
WHERE hp.employee_id = %s
  AND hp.state = 'done'
  AND hp.date_from >= %s
  AND hp.date_to <= %s
  AND hp.id = pl.slip_id
  AND pl.code = %s""", (self.employee_id, from_date, to_date, code))
                res = self.cr.fetchone()
                return res and res[0] or 0.0

        # we keep a dict with the result because a value can be overwritten by
        # another rule with the same code
        result_dict = {}
        rules = {}
        categories_dict = {}
        blacklist = []
        payslip_obj = self.pool.get('hr.payslip')
        obj_rule = self.pool.get('hr.salary.rule')
        payslip = payslip_obj.browse(cr, uid, payslip_id, context=context)
        worked_days = {}
        for worked_days_line in payslip.worked_days_line_ids:
            worked_days[worked_days_line.code] = worked_days_line
        inputs = {}
        for input_line in payslip.input_line_ids:
            inputs[input_line.code] = input_line

        categories_obj = BrowsableObject(
            self.pool, cr, uid, payslip.employee_id.id, categories_dict)
        input_obj = InputLine(
            self.pool, cr, uid, payslip.employee_id.id, inputs)
        worked_days_obj = WorkedDays(
            self.pool, cr, uid, payslip.employee_id.id, worked_days)
        payslip_obj = Payslips(
            self.pool, cr, uid, payslip.employee_id.id, payslip)
        rules_obj = BrowsableObject(
            self.pool, cr, uid, payslip.employee_id.id, rules)

        localdict = {
            'categories': categories_obj,
            'rules': rules_obj,
            'payslip': payslip_obj,
            'worked_days': worked_days_obj,
            'inputs': input_obj,
        }
        # get the ids of the structures on the contracts and their parent id as
        # well
        structure_ids = self.pool.get('hr.contract').get_all_structures(
            cr, uid, contract_ids, context=context)
        # get the rules of the structure and their children
        rule_ids = self.pool.get('hr.payroll.structure').get_all_rules(
            cr, uid, structure_ids, context=context)
        # run the rules by sequence
        sorted_rule_ids = [
            id for id, sequence in sorted(rule_ids, key=lambda x:x[1])]

        rule_pool = self.pool['hr.salary.rule']

        for contract in self.pool.get('hr.contract').browse(
                cr, uid, contract_ids, context=context):
            temp_dict = {}
            utils_dict = self.get_utilities_dict(
                cr, uid, contract, payslip, context=context)
            for k, v in utils_dict.iteritems():
                k_obj = BrowsableObject(
                    self.pool, cr, uid, payslip.employee_id.id, v)
                temp_dict.update({k: k_obj})
            utils_obj = BrowsableObject(
                self.pool, cr, uid, payslip.employee_id.id, temp_dict)
            employee = contract.employee_id
            localdict.update(
                {
                    'employee': employee,
                    'contract': contract,
                    'utils': utils_obj,
                }
            )
            for rule in obj_rule.browse(
                    cr, uid, sorted_rule_ids, context=context):
                key = rule.code + '-' + str(contract.id)
                localdict['result'] = None
                localdict['result_qty'] = 1.0
                # check if the rule can be applied
                if (obj_rule.satisfy_condition(
                        cr, uid, rule.id, localdict, context=context
                ) and rule.id not in blacklist):
                    # compute the amount of the rule
                    amount, qty, rate = obj_rule.compute_rule(
                        cr, uid, rule.id, localdict, context=context
                    )
                    # check if there is already a rule computed with that code
                    previous_amount = rule.code in localdict and localdict[
                        rule.code] or 0.0
                    # set/overwrite the amount computed for this rule in the
                    # localdict
                    tot_rule = amount * qty * rate / 100.0
                    localdict[rule.code] = tot_rule
                    rules[rule.code] = rule
                    # sum the amount for its salary category
                    localdict = _sum_salary_rule_category(
                        localdict,
                        rule.category_id, tot_rule - previous_amount
                    )
                    # create/overwrite the rule in the temporary results
                    result_dict[key] = {
                        'salary_rule_id': rule.id,
                        'contract_id': contract.id,
                        'name': rule.name,
                        'code': rule.code,
                        'category_id': rule.category_id.id,
                        'sequence': rule.sequence,
                        'appears_on_payslip': rule.appears_on_payslip,
                        'condition_select': rule.condition_select,
                        'condition_python': rule.condition_python,
                        'condition_range': rule.condition_range,
                        'condition_range_min': rule.condition_range_min,
                        'condition_range_max': rule.condition_range_max,
                        'amount_select': rule.amount_select,
                        'amount_fix': rule.amount_fix,
                        'amount_python_compute': rule.amount_python_compute,
                        'amount_percentage': rule.amount_percentage,
                        'amount_percentage_base': rule.amount_percentage_base,
                        'register_id': rule.register_id.id,
                        'amount': amount,
                        'employee_id': contract.employee_id.id,
                        'quantity': qty,
                        'rate': rate,
                    }
                else:
                    # blacklist this rule and its children
                    blacklist += [
                        id for id, seq in rule_pool._recursive_search_of_rules(
                            cr, uid, [rule], context=context
                        )
                    ]

        result = [value for code, value in result_dict.items()]
        return result


class hr_payslip_line(orm.Model):

    _name = 'hr.payslip.line'
    _inherit = 'hr.payslip.line'
    _columns = {
        'amount': fields.float(
            'Amount',
            digits_compute=dp.get_precision('Intermediate Payroll'),
        ),
    }


class hr_attendance(orm.Model):

    _name = 'hr.attendance'
    _inherit = 'hr.attendance'

    def _calculate_rollover(self, utcdt, rollover_hours):
        # XXX - assume time part of utcdt is already set to midnight
        return utcdt + timedelta(hours=int(rollover_hours))

    def punches_list_init(
            self, cr, uid, employee_id, pps_template, dFrom, dTo,
            context=None):
        """Returns a dict containing a key for each day in range
        dFrom - dToday and a corresponding tuple containing two list:
        in punches, and the corresponding out punches
        """

        res = []

        # Convert datetime to tz aware datetime according to tz in pay period
        # schedule, then to UTC, and then to naive datetime for comparison with
        # values in db.
        #
        # Also, include records 48 hours previous to and 48 hours after the
        # desired dates so that any requests for rollover, sessions, etc are
        # can be satisfied
        #
        dtFrom = datetime.strptime(
            dFrom.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        dtFrom += timedelta(hours=-48)
        dtTo = datetime.strptime(
            dTo.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        dtTo += timedelta(hours=+48)
        utcdtFrom = timezone(pps_template.tz).localize(
            dtFrom, is_dst=False).astimezone(utc)
        utcdtTo = timezone(pps_template.tz).localize(
            dtTo, is_dst=False).astimezone(utc)
        utcdtDay = utcdtFrom
        utcdtDayEnd = utcdtTo + timedelta(days=+1, seconds=-1)
        ndtDay = utcdtDay.replace(tzinfo=None)
        ndtDayEnd = utcdtDayEnd.replace(tzinfo=None)

        ids = self.search(
            cr, uid, [
                ('employee_id', '=', employee_id),
                '&',
                ('name', '>=', ndtDay.strftime(OE_DATETIMEFORMAT)),
                ('name', '<=', ndtDayEnd.strftime(OE_DATETIMEFORMAT)),
            ], order='name', context=context)

        for a in self.browse(cr, uid, ids, context=context):
            res.append((a.action, a.name))

        return res

    def punches_list_search(
            self, cr, uid, ndtFrom, ndtTo, punches_list, context=None):

        res = []
        for action, name in punches_list:
            ndtName = datetime.strptime(name, OE_DATETIMEFORMAT)
            if ndtFrom <= ndtName <= ndtTo:
                res.append((action, name))
        return res

    def _get_normalized_punches(
            self, cr, uid, employee_id, pps_template, dDay, punches_list,
            context=None):
        """Returns a tuple containing two lists: in punches, and
        corresponding out punches
        """

        #
        # We assume that:
        #    - No dangling sign-in or sign-out
        #

        # Convert datetime to tz aware datetime according to tz in pay period
        # schedule, then to UTC, and then to naive datetime for comparison
        # with values in db.
        #
        dt = datetime.strptime(
            dDay.strftime(OE_DATEFORMAT) + ' 00:00:00', OE_DATETIMEFORMAT)
        utcdtDay = timezone(pps_template.tz).localize(
            dt, is_dst=False).astimezone(utc)
        utcdtDayEnd = utcdtDay + timedelta(days=+1, seconds=-1)
        ndtDay = utcdtDay.replace(tzinfo=None)
        ndtDayEnd = utcdtDayEnd.replace(tzinfo=None)
        my_list = self.punches_list_search(
            cr, uid, ndtDay, ndtDayEnd, punches_list, context=context)
        if len(my_list) == 0:
            return [], []

        # We are assuming attendances are normalized: (in, out, in, out, ...)
        sin = []
        sout = []
        for action, name in my_list:
            if action == 'sign_in':
                sin.append(name)
            elif action == 'sign_out':
                sout.append(name)

        if len(sin) == 0 and len(sout) == 0:
            return [], []

        # CHECKS AT THE START OF THE DAY
        # Remove sessions that would have been included in yesterday's
        # attendance.

        # We may have a a session *FROM YESTERDAY* that crossed-over into
        # today. If it is greater than the maximum continuous hours allowed
        # into the next day (as configured in the pay period schedule), then
        # count only the difference between the actual and the maximum
        # continuous hours.
        #
        dtRollover = (self._calculate_rollover(
            utcdtDay, pps_template.ot_max_rollover_hours)).replace(tzinfo=None)
        if (len(sout) - len(sin)) == 0:

            if len(sout) > 0:
                dtSout = datetime.strptime(sout[0], OE_DATETIMEFORMAT)
                dtSin = datetime.strptime(sin[0], OE_DATETIMEFORMAT)
                if dtSout > dtRollover and (dtSout < dtSin):
                    sin = [dtRollover.strftime(OE_DATETIMEFORMAT)] + sin
                elif dtSout < dtSin:
                    sout = sout[1:]
                    # There may be another session that starts within the
                    # rollover period
                    if (
                        dtSin < dtRollover and
                        float((dtSin - dtSout).seconds) / 60.0 >=
                        pps_template.ot_max_rollover_gap
                    ):
                        sin = sin[1:]
                        sout = sout[1:]
            else:
                return [], []
        elif (len(sout) - len(sin)) == 1:
            dtSout = datetime.strptime(sout[0], OE_DATETIMEFORMAT)
            if dtSout > dtRollover:
                sin = [dtRollover.strftime(OE_DATETIMEFORMAT)] + sin
            else:
                sout = sout[1:]
                # There may be another session that starts within the rollover
                # period
                dtSin = False
                if len(sin) > 0:
                    dtSin = datetime.strptime(sin[0], OE_DATETIMEFORMAT)
                if (
                    dtSin and
                    dtSin < dtRollover and
                    float((dtSin - dtSout).seconds) / 60.0 >=
                        pps_template.ot_max_rollover_gap
                ):
                    sin = sin[1:]
                    sout = sout[1:]

        # If the first sign-in was within the rollover gap *AT* midnight check
        # to see if there are any sessions within the rollover gap before it.
        #
        if len(sout) > 0:
            ndtSin = datetime.strptime(sin[0], OE_DATETIMEFORMAT)
            if (
                (
                    ndtSin - timedelta(
                        minutes=pps_template.ot_max_rollover_gap)
                ) <= ndtDay
            ):
                my_list4 = self.punches_list_search(
                    cr, uid, ndtDay + timedelta(hours=-24),
                    ndtDay + timedelta(seconds=-1), punches_list,
                    context=context
                )
                if len(my_list4) > 0:
                    if my_list4[-1].action == 'sign_out':
                        ndtSout = datetime.strptime(
                            my_list4[-1].name, OE_DATETIMEFORMAT)
                        if ndtSin <= ndtSout + timedelta(
                                minutes=pps_template.ot_max_rollover_gap):
                            sin = sin[1:]
                            sout = sout[1:]

        # CHECKS AT THE END OF THE DAY
        # Include sessions from tomorrow that should be included in today's
        # attendance.

        # We may have a session that crosses the midnight boundary. If so, add
        # it to today's session.
        #
        dtRollover = (self._calculate_rollover(
            ndtDay + timedelta(days=1),
            pps_template.ot_max_rollover_hours
        )).replace(tzinfo=None)
        if (len(sin) - len(sout)) == 1:

            my_list2 = self.punches_list_search(
                cr, uid, ndtDayEnd + timedelta(seconds=+1),
                ndtDayEnd + timedelta(days=1), punches_list, context=context)
            if len(my_list2) == 0:
                name = self.pool.get('hr.employee').read(
                    cr, uid, employee_id, ['name'])['name']
                raise orm.except_orm(
                    _('Attendance Error!'),
                    _('There is not a final sign-out record for %s on %s')
                    % (name, dDay)
                )

            action, name = my_list2[0]
            if action == 'sign_out':
                dtSout = datetime.strptime(name, OE_DATETIMEFORMAT)
                if dtSout > dtRollover:
                    sout.append(dtRollover.strftime(OE_DATETIMEFORMAT))
                else:
                    sout.append(name)
                    # There may be another session within the OT max. rollover
                    # gap
                    if len(my_list2) > 2 and my_list2[1][0] == 'sign_in':
                        dtSin = datetime.strptime(name, OE_DATETIMEFORMAT)
                        if (float((dtSin - dtSout).seconds) / 60.0 <
                                pps_template.ot_max_rollover_gap):
                            sin.append(my_list2[1][1])
                            sout.append(my_list2[2][1])

            else:
                name = self.pool.get('hr.employee').read(
                    cr, uid, employee_id, ['name'])['name']
                raise orm.except_orm(
                    _('Attendance Error!'),
                    _('There is a sign-in with no corresponding sign-out for '
                      '%s on %s') % (name, dDay))

        # If the last sign-out was within the rollover gap *BEFORE* midnight
        # check to see if there are any sessions within the rollover gap after
        # it.
        #
        if len(sout) > 0:
            ndtSout = datetime.strptime(sout[-1], OE_DATETIMEFORMAT)
            if (ndtDayEnd - timedelta(
                    minutes=pps_template.ot_max_rollover_gap)) <= ndtSout:
                my_list3 = self.punches_list_search(
                    cr, uid, ndtDayEnd + timedelta(seconds=+1),
                    ndtDayEnd + timedelta(hours=+24), punches_list,
                    context=context
                )
                if len(my_list3) > 0:
                    action, name = my_list3[0]
                    ndtSin = datetime.strptime(name, OE_DATETIMEFORMAT)
                    if (
                        (ndtSin <= ndtSout + timedelta(
                            minutes=pps_template.ot_max_rollover_gap)) and
                        action == 'sign_in'
                    ):
                        sin.append(name)
                        sout.append(my_list3[1][1])

        return sin, sout

    def _on_day(
            self, cr, uid, contract, dDay, punches_list=None, context=None):
        """Return two lists: the first is sign-in times, and the second
         is corresponding sign-outs."""

        if punches_list is None:
            punches_list = self.punches_list_init(
                cr, uid, contract.employee_id.id, contract.pps_id,
                dDay, dDay, context)

        sin, sout = self._get_normalized_punches(
            cr, uid, contract.employee_id.id, contract.pps_id,
            dDay, punches_list, context=context)
        if len(sin) != len(sout):
            raise orm.except_orm(
                _('Number of Sign-in and Sign-out records do not match!'),
                _('Employee: %s\nSign-in(s): %s\nSign-out(s): %s') %
                (contract.employee_id.name, sin, sout)
            )

        return sin, sout

    def punch_names_on_day(
            self, cr, uid, contract, dDay, punches_list=None, context=None):
        """Return a list of tuples containing in and corresponding out
         punches for the day."""

        sin, sout = self._on_day(
            cr, uid, contract, dDay, punches_list=punches_list, context=context
        )
        return zip(sin, sout)

    def punch_ids_on_day(
            self, cr, uid, contract, dDay, punches_list=None, context=None):
        """Return a list of database ids of punches for the day."""

        sin, sout = self._on_day(
            cr, uid, contract, dDay, punches_list=punches_list, context=context
        )

        names = []
        for i in range(0, len(sin)):
            names.append(sin[i])
            names.append(sout[i])

        return self.search(
            cr, uid, [('employee_id', '=', contract.employee_id.id),
                      ('name', 'in', names)],
            order='name', context=context)

    def total_hours_on_day(
            self, cr, uid, contract, dDay, punches_list=None, context=None):
        """Calculate the number of hours worked on specified date."""

        sin, sout = self._on_day(
            cr, uid, contract, dDay, punches_list=punches_list,
            context=context
        )

        worked_hours = 0
        for i in range(0, len(sin)):
            start = datetime.strptime(sin[i], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(sout[i], '%Y-%m-%d %H:%M:%S')
            worked_hours += float((end - start).seconds) / 60.0 / 60.0

        return worked_hours

    def partial_hours_on_day(
            self, cr, uid, contract, dtDay, active_after, begin, stop, tz,
            punches_list=None, context=None):
        """Calculate the number of hours worked between begin and stop
        hours, but after active_after hours past the beginning of the
        first sign-in on specified date.
        """

        # Since Odoo stores datetime in db as UTC, but in naive format we have
        # to do the following to compare our partial time to the time in db:
        #    1. Make our partial time into a naive datetime
        #    2. Localize the naive datetime to the timezone specified by our
        #       caller
        #    3. Convert our localized datetime to UTC
        #    4. Convert our UTC datetime back into naive datetime format
        #
        dtBegin = datetime.strptime(
            dtDay.strftime(OE_DATEFORMAT) + ' ' + begin + ':00',
            OE_DATETIMEFORMAT
        )
        dtStop = datetime.strptime(
            dtDay.strftime(OE_DATEFORMAT) + ' ' + stop + ':00',
            OE_DATETIMEFORMAT
        )
        if dtStop <= dtBegin:
            dtStop += timedelta(days=1)
        utcdtBegin = timezone(tz).localize(
            dtBegin, is_dst=False).astimezone(utc)
        utcdtStop = timezone(tz).localize(dtStop, is_dst=False).astimezone(utc)
        dtBegin = utcdtBegin.replace(tzinfo=None)
        dtStop = utcdtStop.replace(tzinfo=None)

        if punches_list is None:
            punches_list = self.punches_list_init(
                cr, uid, contract.employee_id.id, contract.pps_id,
                dtDay.date(), dtDay.date(), context)
        sin, sout = self._get_normalized_punches(
            cr, uid, contract.employee_id.id, contract.pps_id,
            dtDay.date(), punches_list, context=context)

        worked_hours = 0
        lead_hours = 0
        for i in range(0, len(sin)):
            start = datetime.strptime(sin[i], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(sout[i], '%Y-%m-%d %H:%M:%S')
            if worked_hours == 0 and end <= dtBegin:
                lead_hours += float((end - start).seconds) / 60.0 / 60.0
            elif worked_hours == 0 and end > dtBegin:
                if start < dtBegin:
                    lead_hours += float(
                        (dtBegin - start).seconds) / 60.0 / 60.0
                    start = dtBegin
                if end > dtStop:
                    end = dtStop
                worked_hours = float((end - start).seconds) / 60.0 / 60.0
            elif worked_hours > 0 and start < dtStop:
                if end > dtStop:
                    end = dtStop
                worked_hours += float((end - start).seconds) / 60.0 / 60.0

        if worked_hours == 0:
            return 0
        elif lead_hours >= active_after:
            return worked_hours

        return max(0, (worked_hours + lead_hours) - active_after)


class hr_contract(orm.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def _hourly(self, cr, uid, ids, field_name, args, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            rate = 0.0
            if contract.wage_type == 'hourly':
                rate = contract.wage
            elif contract.wage_type == 'daily':
                rate = contract.wage / 8.0
            elif contract.wage_type == 'salary':
                rate = contract.wage / 26.0 / 8.0
            res[contract.id] = rate
        return res

    def _daily(self, cr, uid, ids, field_name, args, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            rate = 0.0
            if contract.wage_type == 'hourly':
                rate = contract.wage * 8.0
            elif contract.wage_type == 'daily':
                rate = contract.wage
            elif contract.wage_type == 'salary':
                rate = contract.wage / 26.0
            res[contract.id] = rate
        return res

    def _monthly(self, cr, uid, ids, field_name, args, context=None):

        res = {}
        for contract in self.browse(cr, uid, ids, context=context):
            rate = 0.0
            if contract.wage_type == 'hourly':
                rate = contract.wage * 8.0 * 26.0
            elif contract.wage_type == 'daily':
                rate = contract.wage * 26
            elif contract.wage_type == 'salary':
                rate = contract.wage
            res[contract.id] = rate
        return res

    _columns = {
        'wage_type': fields.selection((('hourly', 'Hourly'),
                                       ('daily', 'Daily'),
                                       ('salary', 'Salary')),
                                      'Wage Type', required=True),
        'wage_hourly': fields.function(
            _hourly,
            type='float',
            digits_compute=dp.get_precision('Intermediate Payroll'),
            string='Hourly Wages',
        ),
        'wage_daily': fields.function(
            _daily,
            type='float',
            digits_compute=dp.get_precision('Intermediate Payroll'),
            string='Daily Wages',
        ),
        'wage_monthly': fields.function(
            _monthly,
            type='float',
            digits_compute=dp.get_precision('Intermediate Payroll'),
            string='Monthly Wages',
        ),
    }

    _defaults = {
        'wage_type': 'salary',
    }


class hr_salary_rule(orm.Model):

    _name = 'hr.salary.rule'
    _inherit = 'hr.salary.rule'

    _columns = {
        'quantity': fields.char(
            'Quantity',
            size=512,
            help="It is used in computation for percentage and fixed amount. "
                 "For e.g. A rule for Meal Voucher having fixed amount of 1€ "
                 "per worked day can have its quantity defined in expression "
                 "like worked_days. "
                 "WORK100.number_of_days.",
        ),
    }


class hr_payslip_worked_days(orm.Model):

    _name = 'hr.payslip.worked_days'
    _inherit = 'hr.payslip.worked_days'

    _columns = {
        'rate': fields.float(
            'Rate',
            required=True,
        ),
    }

    _defaults = {
        'rate': 0.0,
    }
