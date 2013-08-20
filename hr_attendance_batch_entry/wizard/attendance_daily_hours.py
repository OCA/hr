#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
##############################################################################

from datetime import datetime, timedelta
from osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DATETIME_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DATE_FORMAT
from pytz import common_timezones, timezone, utc
import logging
_logger = logging.getLogger(__name__)

class attendance_department(osv.osv_memory):
    
    _name = 'hr.attendance.department'
    _description = 'Weekly Attendance Department Selection'
    
    _columns = {
                'department_id': fields.many2one('hr.department', 'Dept.', readonly=True),
                'line_ids': fields.one2many('hr.attendance.weekly.hours_wizard',
                                            'att_bydept_id',
                                            'Weekly Attendance Lines'),
                'initial_line_ids': fields.one2many('hr.attendance.weekly.hours_wizard',
                                                    'init_att_bydept_id',
                                                    'Initial Attendance Lines'),
    }
    
    def _get_department(self, cr, uid, context=None):
        
        if context == None:
            context= {}
        weekly_id = context.get('active_id', False)
        return  self.pool.get('hr.attendance.weekly').browse(cr, uid, weekly_id, context=context).department_id.id

    def _set_lines_from_records(self, sin, sout, vals):

        # If there are attendance records figure out whether they're for AM or PM.
        # We are aided by this because we know that there will only be max 2 sessions/day.
        # The morning session will be before midday (9:00 UTC).
        #
        # Except for cold room workers, when the first session will be before 1 am.
        #
        am_hours = 0
        pm_hours = 0
        ot_hours = 0
        amhourstart = '07'
        amminstart = '00'
        pmhourstart = '13'
        pmminstart = '00'
        dtCounter = False
        isColdroom = False
        for i in range(0, len(sin)):
            start = datetime.strptime(sin[i], '%Y-%m-%d %H:%M:%S')
            end = datetime.strptime(sout[i], '%Y-%m-%d %H:%M:%S')
            worked_hours = float((end - start).seconds) / 60.0 / 60.0

            midday = datetime.strptime(start.strftime('%Y-%m-%d 9:00:00'), '%Y-%m-%d %H:%M:%S')
            midnight = datetime.strptime(start.strftime('%Y-%m-%d 22:00:00'), '%Y-%m-%d %H:%M:%S')
            
            # Guess whether this is a normal or coldroom attendance by the time
            # of the first punch. Thereafter, set punch hours and minutes according
            # to this guess.
            #
            vals['amhour'] = amhourstart
            vals['ammin'] = amminstart
            vals['pmhour'] = pmhourstart
            vals['pmmin'] = pmminstart
            if not dtCounter and (start < midnight and end >= midnight):
                amhourstart = '21'
                pmhourstart = '02'
                isColdroom = True
            
            if isColdroom:
                midday = midnight
                
            if not dtCounter or dtCounter < midday or dtCounter.weekday() > midday.weekday():
                dtCounter = midday
                am_hours = 0
                pm_hours = 0
                ot_hours = 0
            
            if am_hours == 0 and len(sin) > 2:
                am_hours = worked_hours
            elif am_hours == 0 and start < midday:
                am_hours = worked_hours
            elif am_hours == 0 and start > midday:
                pm_hours = worked_hours
            else:
                pm_hours = worked_hours
            
            if (am_hours + pm_hours) > 8:
                ot_hours = am_hours + pm_hours - 8
                pm_hours -= ot_hours
            
            if midday.weekday() == 0:
                vals['monAM'] = am_hours
                vals['monPM'] = pm_hours
                if ot_hours > 0:
                    vals['monOT1'] = ot_hours
            elif midday.weekday() == 1:
                vals['tueAM'] = am_hours
                vals['tuePM'] = pm_hours
                if ot_hours > 0:
                    vals['tueOT1'] = ot_hours
            elif midday.weekday() == 2:
                vals['wedAM'] = am_hours
                vals['wedPM'] = pm_hours
                if ot_hours > 0:
                    vals['wedOT1'] = ot_hours
            elif midday.weekday() == 3:
                vals['thuAM'] = am_hours
                vals['thuPM'] = pm_hours
                if ot_hours > 0:
                    vals['thuOT1'] = ot_hours
            elif midday.weekday() == 4:
                vals['friAM'] = am_hours
                vals['friPM'] = pm_hours
                if ot_hours > 0:
                    vals['friOT1'] = ot_hours
            elif midday.weekday() == 5:
                vals['satAM'] = am_hours
                vals['satPM'] = pm_hours
                if ot_hours > 0:
                    vals['satOT1'] = ot_hours
            elif midday.weekday() == 6:
                vals['sunAM'] = am_hours
                vals['sunPM'] = pm_hours
                if ot_hours > 0:
                    vals['sunOT1'] = ot_hours
        
        return vals

    def _default_time_vals(self, cr, uid, eid, context=None):
        
        e = self.pool.get('hr.employee').browse(cr, uid, eid, context=context)
        if e.department_id and e.department_id.name.find('Coldroom') != -1:
            res = {'amhour': '21',
                   'ammin': '00',
                   'pmhour': '02',
                   'pmmin': '00',
            }
        else:
            res = {'amhour': '07',
                   'ammin': '00',
                   'pmhour': '13',
                   'pmmin': '00'
            }
        return res
    
    def _get_lines(self, cr, uid, context=None):
        
        if context == None:
            context= {}
        
        e_obj = self.pool.get('hr.employee')
        term_obj = self.pool.get('hr.employee.termination')
        sched_obj = self.pool.get('hr.schedule.detail')
        attendance_obj = self.pool.get('hr.attendance')
        weekly_obj = self.pool.get('hr.attendance.weekly')
        weekly_id = context.get('active_id', False)
        weekly = weekly_obj.browse(cr, uid, weekly_id, context=context)
        res = []
        
        # Get all employees associated with this weekly attendance. This
        # includes current and past employees of the department
        #
        e_ids = e_obj.search(cr, uid,
                             ['|', ('department_id', '=', weekly.department_id.id),
                                   ('saved_department_id', '=', weekly.department_id.id)],
                             context=context)
        att_ids = attendance_obj.search(cr, uid, [('weekly_att_id', '=', weekly_id)],
                                        order='name', context=context)
        e_att_ids = []
        have_att_ids = []
        if len(att_ids) > 0:
            att_data = attendance_obj.read(cr, uid, att_ids, ['employee_id'], context=context)
            for data in att_data:
                if data['employee_id'][0] not in e_ids:
                    e_att_ids.append(data['employee_id'][0])
                    have_att_ids.append(data['employee_id'][0])
            # Re-run it through search() to get correct ordering
            e_ids = e_obj.search(cr, uid, [('id', 'in', e_att_ids + e_ids)], context=context)

        # Remove terminated employees, unless they have an attendance record in this week
        term_ids = term_obj.search(cr, uid, [('employee_id', 'in', e_ids),
                                             ('employee_id.status', 'in', ['pending_inactive', 'inactive']),
                                             ('state', 'in', ['draft','confirm', 'done'])],
                                   context=context)
        if len(term_ids) > 0:
            term_data = term_obj.read(cr, uid, term_ids, ['name', 'employee_id'], context=context)
            for data in term_data:
                if data['name'] < weekly.week_start and data['employee_id'][0] in e_ids and data['employee_id'][0] not in have_att_ids:
                    e_ids.remove(data['employee_id'][0])

        for eid in e_ids:
            vals = {
                    'employee_id': eid,
                    'department_id': weekly.department_id.id,
            }
            
            # Get any attendance records that may already be associated with this timesheet
            #
            sin = []
            sout = []
            att_ids = attendance_obj.search(cr, uid, [('weekly_att_id', '=', weekly_id),
                                                      ('employee_id', '=', eid)],
                                            order='name', context=context)
            
            if len(att_ids) > 0:
                for a in attendance_obj.browse(cr, uid, att_ids, context=context):
                    if a.action == 'sign_in':
                        sin.append(a.name)
                    elif a.action == 'sign_out':
                        sout.append(a.name)
                vals = self._set_lines_from_records(sin, sout, vals)
            else:
                # For the days where there are records, get default values from schedules
                #
                local_tz = timezone('Africa/Addis_Ababa')
                dtStart = datetime.strptime(weekly.week_start + ' 00:00:00', OE_DATETIME_FORMAT)
                utcdtStart = (local_tz.localize(dtStart, is_dst=False)).astimezone(utc)
                utcdtEnd = utcdtStart + timedelta(days=7)
                week_end = utcdtEnd.astimezone(local_tz).strftime(OE_DATE_FORMAT)
                sched_ids = sched_obj.search(cr, uid, [('schedule_id.employee_id', '=', eid),
                                                       ('day', '>=', weekly.week_start),
                                                       ('day', '<', week_end)],
                                             order='date_start', context=context)
                ee_data = e_obj.read(cr, uid, eid, ['status'], context=context)
                term_ids = term_obj.search(cr, uid, [('employee_id', '=', eid),
                                                     ('employee_id.status', 'in', ['pending_inactive', 'inactive']),
                                                     ('state', 'in', ['draft', 'confirm', 'done'])],
                                           context=context)
                if len(term_ids) > 0:
                    term_data = term_obj.read(cr, uid, term_ids[0], ['name'], context=context)
                else:
                    term_data = False
                worked_days = []
                week_days = [0, 1, 2, 3, 4, 5, 6]
                dTempSaved = False
                for s in sched_obj.browse(cr, uid, sched_ids, context=context):

                    # Break if the employee no longer works for us
                    dTerm = term_data and datetime.strptime(term_data['name'], OE_DATE_FORMAT).date() or False
                    dToday = datetime.strptime(s.date_start, OE_DATETIME_FORMAT).date()
                    if term_data and ee_data['status'] in ['pending_inactive', 'inactive'] and dTerm < dToday:
                        vals.update(self._default_time_vals(cr, uid, eid, context=context))
                        break

                    # If we have a partial record for this employee on this date, use it
                    #
                    ispartial = False
                    worked_days.append(int(s.dayofweek))
                    dTemp = datetime.strptime(s.date_start, OE_DATETIME_FORMAT).date()
                    for partial in weekly.partial_ids:
                        dPartial = datetime.strptime(partial.date, OE_DATE_FORMAT).date()
                        if dPartial == dTemp and partial.employee_id.id == eid:
                            ispartial = True
                            dt_sched_start = datetime.strptime(s.date_start, OE_DATETIME_FORMAT)
                            if (dTempSaved == False or dTempSaved != dTemp):
                                if partial.s1hours > 0.01:
                                    dt_sched_end = dt_sched_start + timedelta(seconds= +int(partial.s1hours * 60.0 * 60.0))
                                    sin.append(dt_sched_start.strftime(OE_DATETIME_FORMAT))
                                    sout.append(dt_sched_end.strftime(OE_DATETIME_FORMAT))
                            elif dTempSaved == dTemp:
                                if partial.s2hours > 0.01:
                                    dt_sched_end = dt_sched_start + timedelta(seconds= +int(partial.s2hours * 60.0 * 60.0))
                                    sin.append(dt_sched_start.strftime(OE_DATETIME_FORMAT))
                                    sout.append(dt_sched_end.strftime(OE_DATETIME_FORMAT))
                            dTempSaved = dTemp
                            break
                    
                    # There is no partial record, use the date/times in the schedule
                    #
                    if not ispartial:
                        # Add OT hours to regular schedule
                        dt = datetime.strptime(s.date_start, OE_DATETIME_FORMAT)
                        dtE = datetime.strptime(s.date_end, OE_DATETIME_FORMAT)
                        date_start = s.date_start
                        date_end = s.date_end
                        otHours = 0.0
                        for ot in weekly.ot_ids:
                            if ot.employee_id.id == s.schedule_id.employee_id.id:
                                if dt.weekday() == 0 and ot.mon > 0.01:
                                    otHours = ot.mon
                                elif dt.weekday() == 1 and ot.tue > 0.01:
                                    otHours = ot.tue
                                elif dt.weekday() == 2 and ot.wed > 0.01:
                                    otHours = ot.wed
                                elif dt.weekday() == 3 and ot.thu > 0.01:
                                    otHours = ot.thu
                                elif dt.weekday() == 4 and ot.fri > 0.01:
                                    otHours = ot.fri
                                elif dt.weekday() == 5 and ot.sat > 0.01:
                                    otHours = ot.sat
                                elif dt.weekday() == 6 and ot.sun > 0.01:
                                    otHours = ot.sun
                        if otHours > 0.01:
                            # Figure out if this is the last entry for the day, and if it
                            # is add the OT hours to it
                            detail_ids = sched_obj.search(cr, uid, [('schedule_id.employee_id', '=', eid),
                                                                    ('day', '=', s.day)],
                                                          order='date_start', context=context)
                            data = sched_obj.read(cr, uid, detail_ids[-1], ['date_start', 'date_end'],
                                                  context=context)
                            if data['date_start'] == s.date_start:
                                dtE = datetime.strptime(data['date_end'], OE_DATETIME_FORMAT)
                                dtE += timedelta(hours= otHours)
                                date_end = dtE.strftime(OE_DATETIME_FORMAT)
                        
                        if not self.on_leave(cr, uid, eid, dt, context=context) and not self.on_leave(cr, uid, eid, dtE, context=context):
                            sin.append(date_start)
                            sout.append(date_end)
                
                if len(sched_ids) > 0:
                    # Add OT hours for any days not in the schedule
                    #
                    rest_days = [d for d in week_days if d not in worked_days]
                    for d in rest_days:
                        otHours = 0.0
                        for ot in weekly.ot_ids:
                            if ot.employee_id.id == eid:
                                if d == 0 and ot.mon > 0.01:
                                    otHours = ot.mon
                                elif d == 1 and ot.tue > 0.01:
                                    otHours = ot.tue
                                elif d == 2 and ot.wed > 0.01:
                                    otHours = ot.wed
                                elif d == 3 and ot.thu > 0.01:
                                    otHours = ot.thu
                                elif d == 4 and ot.fri > 0.01:
                                    otHours = ot.fri
                                elif d == 5 and ot.sat > 0.01:
                                    otHours = ot.sat
                                elif d == 6 and ot.sun > 0.01:
                                    otHours = ot.sun
                        if otHours > 0.01:
                            employee = e_obj.browse(cr, uid, eid, context=context)
                            if employee.department_id and employee.department_id.name.find('Coldroom') != -1:
                                times = ['21:00:00', '01:00:00', '02:00:00', '06:00:00']
                            else:
                                times = ['07:00:00', '12:00:00', '13:00:00', '16:00:00']
                            dtWeek = datetime.strptime(weekly.week_start +' '+ times[0], OE_DATETIME_FORMAT)
                            dtAM = dtWeek + timedelta(days= d)
                            local_tz = timezone(employee.contract_id.pps_id.tz)
                            utcdtAM = (local_tz.localize(dtAM, is_dst=False)).astimezone(utc)
                            if otHours > 6.0:
                                utcdtAMend = utcdtAM + timedelta(hours= 5)
                                utcdtPM = utcdtAMend + timedelta(hours= +1)
                                utcdtPMend = utcdtPM + timedelta(hours= (otHours - 5))
                            else:
                                utcdtAMend = utcdtAM + timedelta(hours= otHours)
                                utcdtPM = False
                                utcdtPMend = False
                            if not self.on_leave(cr, uid, eid, utcdtAM, context=context) and not self.on_leave(cr, uid, eid, utcdtAMend, context=context):
                                sin.append(utcdtAM.strftime(OE_DATETIME_FORMAT))
                                sout.append(utcdtAMend.strftime(OE_DATETIME_FORMAT))
                            if utcdtPM and (not self.on_leave(cr, uid, eid, utcdtPM, context=context) and not self.on_leave(cr, uid, eid, utcdtPMend, context=context)):
                                sin.append(utcdtPM.strftime(OE_DATETIME_FORMAT))
                                sout.append(utcdtPMend.strftime(OE_DATETIME_FORMAT))
                    
                    vals = self._set_lines_from_records(sin, sout, vals)
                else:
                    # There is no schedule, either
                    vals.update(self._default_time_vals(cr, uid, eid, context=context))
                
            res.append(vals)
        return res
    
    _defaults = {
                 'department_id': _get_department,
                 'line_ids': _get_lines,
                 'initial_line_ids': _get_lines,
                 }
    
    def on_leave(self, cr, uid, employee_id, utcdt, context=None):
        
        str_dt = utcdt.strftime(OE_DATETIME_FORMAT)
        leave_ids = self.pool.get('hr.holidays').search(cr, uid, [('employee_id', '=', employee_id),
                                                                  ('type', '=', 'remove'),
                                                                  ('date_from', '<=', str_dt),
                                                                  ('date_to', '>=', str_dt),
                                                                  ('state', 'in', ['validate', 'validate1'])],
                                                        context=context)
        return (len(leave_ids) > 0)
    
    def get_action_reason(self, cr, uid, reason, text, context=None):
        
        aid = self.pool.get('hr.action.reason').search(cr, uid, [
                                                                ('action_type', '=', reason),
                                                                ('name', 'ilike', text),
                                                               ],
                                                      context=context)
        if len(aid) == 0:
            return False
        return aid[0]
    
    def add_AM(self, cr, uid, employee_id, delta, local_tz, dNextDay, sinDesc, soutDesc,
               hrStart, minStart, punches):
        if not delta or delta < 0.01:
            return punches
        
        sinTime = datetime.strptime(dNextDay.strftime("%Y-%m-%d") + " " +
                                    hrStart + ":" + minStart + ":00", "%Y-%m-%d %H:%M:%S")
        utcSinTime = (local_tz.localize(sinTime, is_dst=False)).astimezone(utc)
        soutTime = sinTime + timedelta(hours=delta)
        utcSoutTime = (local_tz.localize(soutTime, is_dst=False)).astimezone(utc)
        
        # Second attempt at catching attempts to modify attendance for locked periods.
        # This will catch attendances erroneously inserted where there was no previous
        # attendance data for the week.
        #
        att_obj = self.pool.get('hr.attendance')
        if att_obj.is_locked(cr, uid, employee_id, utcSinTime.strftime(OE_DATETIME_FORMAT)):
            return punches
        
        recIn = {
               'name': utcSinTime.strftime("%Y-%m-%d %H:%M:%S"),
               'action': 'sign_in',
               'action_desc': sinDesc,
               'employee_id': employee_id
        }
        recOut = {
               'name': utcSoutTime.strftime("%Y-%m-%d %H:%M:%S"),
               'action': 'sign_out',
               'action_desc': soutDesc,
               'employee_id': employee_id
        }
        punches.append(recIn)
        punches.append(recOut)
        return punches
    
    def add_PM(self, cr, uid, employee_id, delta, deltaOT, local_tz, dNextDay, sinDesc, soutDesc,
               hrStart, minStart, amhrStart, amminStart, punches):
        if not delta or delta < 0.01:
            return punches
        
        deltaCalc = datetime.strptime(hrStart+':'+minStart, '%H:%M') - datetime.strptime(amhrStart+':'+amminStart, '%H:%M')
        sinTime = datetime.strptime(dNextDay.strftime("%Y-%m-%d") + " " +
                                    amhrStart + ":" + amminStart + ":00", "%Y-%m-%d %H:%M:%S")
        utcSinTime = (local_tz.localize(sinTime, is_dst=False)).astimezone(utc)
        utcSinTime += timedelta(seconds=deltaCalc.seconds)
        
        # Second attempt at catching attempts to modify attendance for locked periods.
        # This will catch attendances erroneously inserted where there was no previous
        # attendance data for the week.
        #
        att_obj = self.pool.get('hr.attendance')
        if att_obj.is_locked(cr, uid, employee_id, utcSinTime.strftime(OE_DATETIME_FORMAT)):
            return punches
        
        if deltaOT < 0.01:
            utcSoutTime = utcSinTime + timedelta(hours=delta)
        else:
            utcSoutTime = utcSinTime + timedelta(hours=(delta + deltaOT))
        recIn = {
               'name': utcSinTime.strftime("%Y-%m-%d %H:%M:%S"),
               'action': 'sign_in',
               'action_desc': sinDesc,
               'employee_id': employee_id
        }
        recOut = {
               'name': utcSoutTime.strftime("%Y-%m-%d %H:%M:%S"),
               'action': 'sign_out',
               'action_desc': soutDesc,
               'employee_id': employee_id
        }
        punches.append(recIn)
        punches.append(recOut)
        return punches

    def add_records(self, cr, uid, ids, context=None):
        """Add a week's worth of attendance hours for all employees in a department"""
        
        if context == None:
            context = {}
        
        local_tz = timezone('Africa/Addis_Ababa')
        weekly_obj = self.pool.get('hr.attendance.weekly')
        data = self.read(cr, uid, ids[0], ['id', 'line_ids', 'initial_line_ids'], context=context)
        weekly_id = context.get('active_id', False)
        line_ids = data['line_ids']
        
        ee_ids = []
        lines = self.pool.get('hr.attendance.weekly.hours_wizard').browse(cr, uid, line_ids, context=context)
        init_lines = self.pool.get('hr.attendance.weekly.hours_wizard').browse(cr, uid, data['initial_line_ids'],
                                                                               context=context)
        for line in lines:
            if line.employee_id.id not in ee_ids:
                ee_ids.append(line.employee_id.id)
        
        count = -1
        weekly = weekly_obj.browse(cr, uid, weekly_id, context=context)
        for lid in lines:
            
            # If the line has changed them remove the entire attendance for the week for
            # that employee, otherwise, continue to the next line
            #
            count +=1
            days = []
            if self.line_is_changed(cr, uid, lid.employee_id.contract_id, weekly.week_start,
                                    lid, init_lines[count], context=context):
                days = self.remove_attendance(cr, uid, weekly.week_start, lid, context=context)
            else:
                continue
            
            sinDesc = self.get_action_reason(cr, uid, 'sign_in', 'Batch Sign-in%', context=context)
            soutDesc = self.get_action_reason(cr, uid, 'sign_out', 'Batch Sign-out%', context=context)
            dNextDay = datetime.strptime(weekly.week_start, "%Y-%m-%d").date()
            punches = []
            
            # Monday
            if 0 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.monAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.monPM, lid.monOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            # Tuesday
            if 1 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.tueAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.tuePM, lid.tueOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            # Wednesday
            if 2 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.wedAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.wedPM, lid.wedOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            # Thursday
            if 3 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.thuAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.thuPM, lid.thuOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            # Friday
            if 4 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.friAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.friPM, lid.friOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            # Saturday
            if 5 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.satAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.satPM, lid.satOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            # Sunday
            if 6 in days:
                punches = self.add_AM(cr, uid, lid.employee_id.id, lid.sunAM, local_tz,
                                      dNextDay, sinDesc, soutDesc, lid.amhour, lid.ammin, punches)
                punches = self.add_PM(cr, uid, lid.employee_id.id, lid.sunPM, lid.sunOT1, local_tz, dNextDay,
                                      sinDesc, soutDesc, lid.pmhour, lid.pmmin, lid.amhour, lid.ammin, punches)
            dNextDay += timedelta(days=1)
            
            [weekly_obj.write(cr, uid, weekly_id, {'att_ids': [(0, 0, punch)]}, context=context) for punch in punches]
        
        return {'type': 'ir.actions.act_window_close'}

    def line_is_changed(self, cr, uid, contract, week_start, curr, init, context=None):
        
        res = False
        count = 0
        d = datetime.strptime(week_start, OE_DATE_FORMAT)
        monHours = curr.monAM + curr.monPM + curr.monOT1
        tueHours = curr.tueAM + curr.tuePM + curr.tueOT1
        wedHours = curr.wedAM + curr.wedPM + curr.wedOT1
        thuHours = curr.thuAM + curr.thuPM + curr.thuOT1
        friHours = curr.friAM + curr.friPM + curr.friOT1
        satHours = curr.satAM + curr.satPM + curr.satOT1
        sunHours = curr.sunAM + curr.sunPM + curr.sunOT1
        while count < 7:
            hours = self.pool.get('hr.attendance').total_hours_on_day(cr, uid, contract,
                                                                      d + timedelta(days= count),
                                                                      context=context)
            if count == 0 and (hours > monHours or hours < monHours or curr.monAM != init.monAM or curr.monPM != init.monPM or curr.monOT1 != init.monOT1):
                res = True
            elif count == 1 and (hours > tueHours or hours < tueHours or curr.tueAM != init.tueAM or curr.tuePM != init.tuePM or curr.tueOT1 != init.tueOT1):
                res = True
            elif count == 2 and (hours > wedHours or hours < wedHours or curr.wedAM != init.wedAM or curr.wedPM != init.wedPM or curr.wedOT1 != init.wedOT1):
                res = True
            elif count == 3 and (hours > thuHours or hours < thuHours or curr.thuAM != init.thuAM or curr.thuPM != init.thuPM or curr.thuOT1 != init.thuOT1):
                res = True
            elif count == 4 and (hours > friHours or hours < friHours or curr.friAM != init.friAM or curr.friPM != init.friPM or curr.friOT1 != init.friOT1):
                res = True
            elif count == 5 and (hours > satHours or hours < satHours or curr.satAM != init.satAM or curr.satPM != init.satPM or curr.satOT1 != init.satOT1):
                res = True
            elif count == 6 and (hours > sunHours or hours < sunHours or curr.sunAM != init.sunAM or curr.sunPM != init.sunPM or curr.sunOT1 != init.sunOT1):
                res = True
                
            count += 1
            
        return res
    
    def remove_attendance(self, cr, uid, week_start, lid, context=None):
        
        att_obj = self.pool.get('hr.attendance')
        
        days_removed = []
        count = 0
        d = datetime.strptime(week_start, OE_DATE_FORMAT)
        while count < 7:
            
            # Remove each day's records one day at a time. If there are any locked records
            # do not remove *any* records for the day.
            #
            ids = att_obj.punch_ids_on_day(cr, uid, lid.employee_id.contract_id,
                                           d + timedelta(days= count), context=context)
            unlocked_ids = []
            for att in att_obj.browse(cr, uid, ids, context=context):
                if att.state != 'locked':
                    unlocked_ids.append(att.id)
                else:
                    unlocked_ids = []
                    break
            
            if len(unlocked_ids) > 0:
                att_obj.unlink(cr, uid, unlocked_ids, context=context)
                days_removed.append(count)
            elif len(ids) == 0:
                # XXX - my (complicated) attempt at trying not to erroneously include rest
                #       days (with no attendances) that fall between two locked days.
                att_next = False
                next_ids = []
                _count = 1
                while len(next_ids) == 0 and _count < 7:
                    next_ids = att_obj.punch_ids_on_day(cr, uid, lid.employee_id.contract_id,
                                                    d + timedelta(days= (count + _count)), context=context)
                    _count += 1
                if len(next_ids) > 0:
                    att_next = att_obj.browse(cr, uid, next_ids[0], context=context)
                if not att_next or att_next.state != 'locked':
                    days_removed.append(count)
            
            count += 1
        
        return days_removed
        
attendance_department()

class attendance_daily_hours(osv.osv_memory):
    
    _name = 'hr.attendance.weekly.hours_wizard'
    _description = "Weekly Attendance"
    
    _columns = {
                'employee_id': fields.many2one('hr.employee', 'Employee', required=True,
                                               readonly=True),
                'department_id': fields.many2one('hr.department', 'Department'),
                'amhour': fields.char('Start Hour', size=2),
                'ammin': fields.char('Start Min.', size=2),
                'pmhour': fields.char('Start Hour', size=2),
                'pmmin': fields.char('Start Min.', size=2),
                'monAM': fields.float('Mon AM', required=True),
                'monPM': fields.float('Mon PM', required=True),
                'monOT1': fields.float('OT'),
                'tueAM': fields.float('Tue AM', required=True),
                'tuePM': fields.float('Tue PM', required=True),
                'tueOT1': fields.float('OT'),
                'wedAM': fields.float('Wed AM', required=True),
                'wedPM': fields.float('Wed PM', required=True),
                'wedOT1': fields.float('OT'),
                'thuAM': fields.float('Thu AM', required=True),
                'thuPM': fields.float('Thu PM', required=True),
                'thuOT1': fields.float('OT'),
                'friAM': fields.float('Fri AM', required=True),
                'friPM': fields.float('Fri PM', required=True),
                'friOT1': fields.float('OT'),
                'satAM': fields.float('Sat AM', required=True),
                'satPM': fields.float('Sat PM', required=True),
                'satOT1': fields.float('OT'),
                'sunAM': fields.float('Sun AM', required=True),
                'sunPM': fields.float('Sun PM', required=True),
                'sunOT1': fields.float('OT'),
                'att_bydept_id': fields.many2one('hr.attendance.department',
                                                 'Weekly Attendance by Department'),
                'init_att_bydept_id': fields.many2one('hr.attendance.department',
                                                      'Weekly Attendance by Department'),
    }
    
    _defaults = {
                 'monAM': 0,
                 'monPM': 0,
                 'tueAM': 0,
                 'tuePM': 0,
                 'wedAM': 0,
                 'wedPM': 0,
                 'thuAM': 0,
                 'thuPM': 0,
                 'friAM': 0,
                 'friPM': 0,
                 'satAM': 0,
                 'satPM': 0,
                 'sunAM': 0,
                 'sunPM': 0,
    }

attendance_daily_hours()
