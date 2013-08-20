#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
from pytz import timezone, utc

from osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT as OE_DTFORMAT
from tools.translate import _

class hr_attendance_weekly(osv.osv):
    
    _name = 'hr.attendance.weekly'
    _description = 'Weekly Attendance'
    
    _columns = {
                'att_ids': fields.one2many('hr.attendance', 'weekly_att_id', 'Daily Attendance Records', readonly=True),
                'department_id': fields.many2one('hr.department', 'Department', required=True),
                'week_start': fields.date('Start of Week', required=True),
                'partial_ids': fields.one2many('hr.attendance.weekly.partial', 'weekly_id', 'Partial Attendance'),
                'ot_ids': fields.one2many('hr.attendance.weekly.ot', 'weekly_id', 'Over-Time'),
    }
    
    _rec_name = 'week_start'
    
    _order = 'week_start desc, department_id'
    
    _sql_constraints = [
                ('week_dept_uniq', 'UNIQUE(week_start, department_id)', 'Duplicate record!'),
    ]
    
    def onchange_department(self, cr, uid, ids, department_id, context=None):
        
        res = {}
        self.action_delete_hours(cr, uid, ids, context=context)
        return res
    
    def onchange_week_start(self, cr, uid, ids, newdate, context=None):
        
        res = {'value': {'week_start': newdate}}
        if newdate:
            d = datetime.strptime(newdate, "%Y-%m-%d")
            if d.weekday() != 0:
                res['value']['week_start'] = False
                return res
        self.action_delete_hours(cr, uid, ids, context=context)
        return res
    
    def button_delete_hours(self, cr, uid, ids, context=None):
        
        return self.action_delete_hours(cr, uid, ids, context=None)
    
    def action_delete_hours(self, cr, uid, ids, employee_ids=None, context=None):
        
        att_obj = self.pool.get('hr.attendance')
        
        domain = [('weekly_att_id', 'in', ids)]
        if employee_ids != None:
            domain = domain + [('employee_id.id', 'in', employee_ids)]
        
        att_ids = att_obj.search(cr, uid, domain, context=context)
        att_obj.unlink(cr, uid, att_ids, context=context)
        return True

class hr_weekly_absent(osv.Model):
    
    _name = 'hr.attendance.weekly.partial'
    _description = 'Weekly Attendance Employee absence records'
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'weekly_id': fields.many2one('hr.attendance.weekly', 'Weekly Attendance', required=True),
        'dayofweek': fields.selection([('0', 'Monday'),('1', 'Tuesday'),
                                       ('2', 'Wednesday'),('3', 'Thursday'),
                                       ('4', 'Friday'),('5', 'Saturday'),
                                       ('6', 'Sunday')],
                                      'Day of Week'),
        'date': fields.date('Date', required=True),
        's1hours': fields.float('First Shift', help="Hours worked in morning shift."),
        's2hours': fields.float('Second Shift', help="Hours worked in afternoon shift."),
    }
    
    def _get_weekly(self, cr, uid, context=None):
        
        if context == None:
            context = {}
        
        return context.get('weekly_id', False)
    
    _defaults = {
        'weekly_id': _get_weekly,
    }
    
    def onchange_dayofweek(self, cr, uid, ids, weekly_id, dayofweek, date_str, context=None):
        
        res = {'value': {'date': False}}
        if not dayofweek:
            return res
        
        weekly = self.pool.get('hr.attendance.weekly').browse(cr, uid, weekly_id, context=context)
        d = datetime.strptime(weekly.week_start, OE_DFORMAT)
        d = d + timedelta(days= +int(dayofweek))
        res['value']['date'] = d.strftime(OE_DFORMAT)
        
        return res
    
    def create(self, cr, uid, vals, context=None):
        
        res = super(hr_weekly_absent, self).create(cr, uid, vals, context=context)
        
        att_obj = self.pool.get('hr.attendance')
        
        # Get attendance records for the day and sort them properly
        #
        att_ids = []
        att_list = []
        partial = self.browse(cr, uid, res, context=context)
        for attendance in partial.weekly_id.att_ids:
            if attendance.employee_id.id == partial.employee_id.id and attendance.day == partial.date:
                att_ids.append(attendance.id)
        if len(att_ids) == 0:
            return res
        att_ids = att_obj.search(cr, uid, [('id', 'in', att_ids)], order='name', context=context)
        for attendance in att_obj.browse(cr, uid, att_ids, context=context):
            att_list.append(attendance)
        
        # If no hours on the day, delete all attendances for that day
        att_ids = []
        if (not partial.s1hours or (partial.s1hours > -0.01 and partial.s1hours < 0.01)) and (not partial.s2hours or (partial.s2hours > -0.01 and partial.s2hours < 0.01)):
            [att_ids.append(att.id) for att in att_list]
            att_obj.unlink(cr, uid, att_ids, context=context)
            return res
    
        morning = False
        afternoon = False
        if len(att_list) > 1:
            morning = (att_list[0], att_list[1])
        if len(att_list) > 3:
            afternoon = (att_list[2], att_list[3])
        
        # Employee was only partialy absent (morning)
        attstart, attend = morning
        if (partial.s1hours != False and partial.s1hours > 0.01):
            dtend = datetime.strptime(attend.name, OE_DTFORMAT)
            dtstart = dtend + timedelta(hours= -partial.s1hours)
            att_obj.write(cr, uid, attstart.id, {'name': dtstart.strftime(OE_DTFORMAT)},
                          context=context)
        else:
            att_obj.unlink(cr, uid, [attstart.id, attend.id], context=context)
        
        # Employee was only partially absent (afternoon)
        attstart, attend = afternoon
        if (partial.s2hours != False and partial.s2hours > 0.01):
            dtstart = datetime.strptime(attstart.name, OE_DTFORMAT)
            dtend = dtstart + timedelta(hours= +partial.s2hours)
            att_obj.write(cr, uid, attend.id, {'name': dtend.strftime(OE_DTFORMAT)},
                          context=context)
        else:
            att_obj.unlink(cr, uid, [attstart.id, attend.id], context=context)
        
        return res

class hr_weekly_ot(osv.Model):
    
    _name = 'hr.attendance.weekly.ot'
    _description = 'Weekly Attendance OT Record'
    
    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'weekly_id': fields.many2one('hr.attendance.weekly', 'Weekly Attendance', required=True),
        'mon': fields.float('Mon'),
        'tue': fields.float('Tue'),
        'wed': fields.float('Wed'),
        'thu': fields.float('Thu'),
        'fri': fields.float('Fri'),
        'sat': fields.float('Sat'),
        'sun': fields.float('Sun'),
    }
    
    def _get_weekly(self, cr, uid, context=None):
        
        if context == None:
            context = {}
        
        return context.get('weekly_id', False)
    
    _defaults = {
        'weekly_id': _get_weekly,
    }
    
    def get_action_reason(self, cr, uid, reason, text, context=None):
        
        aid = self.pool.get('hr.action.reason').search(cr, uid, [
                                                                ('action_type', '=', reason),
                                                                ('name', 'ilike', text),
                                                               ],
                                                      context=context)
        if len(aid) == 0:
            return False
        return aid[0]
    
    def _modify_attendance(self, cr, uid, employee, wid, week_start, day, otHours,
                           attendance_list, subtract=False, context=None):
        
        att_obj = self.pool.get('hr.attendance')
        
        shift1 = 5
        weekday = {'mon': 0, 'tue': 1, 'wed': 2, 'thu': 3, 'fri': 4, 'sat': 5, 'sun': 6}
        inDesc = self.get_action_reason(cr, uid, 'sign_in', 'Batch Sign-in%', context=context)
        outDesc = self.get_action_reason(cr, uid, 'sign_out', 'Batch Sign-out%', context=context)
        if len(attendance_list) > 0:
            dtStart = datetime.strptime(attendance_list[-2].name, OE_DTFORMAT)
            dtEnd = datetime.strptime(attendance_list[-1].name, OE_DTFORMAT)
            dtEnd += timedelta(hours= otHours)
            if subtract:
                
                # OT to subtract crosses shift boundaries
                counter = 2
                while dtEnd <= dtStart and len(attendance_list) >= counter:
                    dtCurrStart = datetime.strptime(attendance_list[-(counter)].name, OE_DTFORMAT)
                    att_obj.unlink(cr, uid, [attendance_list[-(counter - 1)].id,
                                             attendance_list[-(counter)].id],
                                   context=context)
                    if counter == len(attendance_list):
                        break
                    
                    counter += 2
                    dtStart = datetime.strptime(attendance_list[-(counter)].name, OE_DTFORMAT)
                    dtPrevEnd = datetime.strptime(attendance_list[-(counter - 1)].name, OE_DTFORMAT)
                    
                    # Extend original end time by any break/lunch time in between
                    dtEnd -= dtCurrStart - dtPrevEnd
                
                # OT to subtract is less than the last shift
                if dtEnd > dtStart:
                    att_obj.write(cr, uid, attendance_list[-(counter -1)].id,
                                  {'name': dtEnd.strftime(OE_DTFORMAT)}, context=context)
            else:
                att_obj.write(cr, uid, attendance_list[-1].id,
                              {'name': dtEnd.strftime(OE_DTFORMAT)}, context=context)
        elif not subtract:
            if employee.department_id and employee.department_id.name.find('Coldroom') != -1:
                times = ['21:00:00', '01:00:00', '02:00:00', '06:00:00']
                shift1 = 4
            else:
                times = ['07:00:00', '12:00:00', '13:00:00', '16:00:00']
            dtWeek = datetime.strptime(week_start +' '+ times[0], OE_DTFORMAT)
            dtAM = dtWeek + timedelta(days= weekday[day])
            local_tz = timezone(employee.contract_id.pps_id.tz)
            utcdtAM = (local_tz.localize(dtAM, is_dst=False)).astimezone(utc)
            if otHours > 6.0:
                utcdtAMend = utcdtAM + timedelta(hours= shift1)
                utcdtPM = utcdtAMend + timedelta(hours= +1)
                utcdtPMend = utcdtPM + timedelta(hours= (otHours - shift1))
            else:
                utcdtAMend = utcdtAM + timedelta(hours= otHours)
                utcdtPM = False
                utcdtPMend = False
            
            inPM = False
            outPM = False
            inAM = {
                   'name': utcdtAM.strftime(OE_DTFORMAT),
                   'action': 'sign_in',
                   'action_desc': inDesc,
                   'employee_id': employee.id,
                   'weekly_att_id': wid,
            }
            outAM = {
                   'name': utcdtAMend.strftime(OE_DTFORMAT),
                   'action': 'sign_out',
                   'action_desc': outDesc,
                   'employee_id': employee.id,
                   'weekly_att_id': wid,
            }
            if utcdtPM:
                inPM = {
                       'name': utcdtPM.strftime(OE_DTFORMAT),
                       'action': 'sign_in',
                       'action_desc': inDesc,
                       'employee_id': employee.id,
                       'weekly_att_id': wid,
                }
                outPM = {
                       'name': utcdtPMend.strftime(OE_DTFORMAT),
                       'action': 'sign_out',
                       'action_desc': outDesc,
                       'employee_id': employee.id,
                       'weekly_att_id': wid,
                }
            
            att_obj.create(cr, uid, inAM, context=context)
            att_obj.create(cr, uid, outAM, context=context)
            if inPM:
                att_obj.create(cr, uid, inPM, context=context)
                att_obj.create(cr, uid, outPM, context=context)
    
    def get_punch_dict(self, cr, uid, ot_id, context=None):
        
        att_obj = self.pool.get('hr.attendance')
        weekly_punches = {
            'mon': [],
            'tue': [],
            'wed': [],
            'thu': [],
            'fri': [],
            'sat': [],
            'sun': [],
        }
        
        # Get attendance records for the day and sort them properly
        #
        att_ids = []
        att_list = []
        ot = self.browse(cr, uid, ot_id, context=context)
        for attendance in ot.weekly_id.att_ids:
            if attendance.employee_id.id == ot.employee_id.id:
                att_ids.append(attendance.id)
        if len(att_ids) == 0:
            return weekly_punches
        att_ids = att_obj.search(cr, uid, [('id', 'in', att_ids)], order='name', context=context)
        for attendance in att_obj.browse(cr, uid, att_ids, context=context):
            att_list.append(attendance)
        
        # Sort out which punches belong to which days
        #
        for att in att_list:
            dt = datetime.strptime(att.name, OE_DTFORMAT)
            if dt.weekday() == 0:
                weekly_punches['mon'].append(att)
            elif dt.weekday() == 1:
                weekly_punches['tue'].append(att)
            elif dt.weekday() == 2:
                weekly_punches['wed'].append(att)
            elif dt.weekday() == 3:
                weekly_punches['thu'].append(att)
            elif dt.weekday() == 4:
                weekly_punches['fri'].append(att)
            elif dt.weekday() == 5:
                weekly_punches['sat'].append(att)
            elif dt.weekday() == 6:
                weekly_punches['sun'].append(att)
        
        return weekly_punches
    
    def process_attendance(self, cr, uid, ot_id, subtract=False, context=None):
        
        ot = self.browse(cr, uid, ot_id, context=context)
        weekly_punches = self.get_punch_dict(cr, uid, ot_id, context=context)
        if weekly_punches == None:
            return
        
        # If there are OT hours for a particular day modify the attendanc records accordingly
        if ot.mon and ot.mon > 0.01:
            hours = subtract and -(ot.mon) or ot.mon
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'mon', hours, weekly_punches['mon'], subtract=subtract, context=context)
        if ot.tue and ot.tue > 0.01:
            hours = subtract and -(ot.tue) or ot.tue
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'tue', hours, weekly_punches['tue'], subtract=subtract, context=context)
        if ot.wed and ot.wed > 0.01:
            hours = subtract and -(ot.wed) or ot.wed
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'wed', hours, weekly_punches['wed'], subtract=subtract, context=context)
        if ot.thu and ot.thu > 0.01:
            hours = subtract and -(ot.thu) or ot.thu
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'thu', hours, weekly_punches['thu'], subtract=subtract, context=context)
        if ot.fri and ot.fri > 0.01:
            hours = subtract and -(ot.fri) or ot.fri
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'fri', hours, weekly_punches['fri'], subtract=subtract, context=context)
        if ot.sat and ot.sat > 0.01:
            hours = subtract and -(ot.sat) or ot.sat
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'sat', hours, weekly_punches['sat'], subtract=subtract, context=context)
        if ot.sun and ot.sun > 0.01:
            hours = subtract and -(ot.sun) or ot.sun
            self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id, ot.weekly_id.week_start,
                                    'sun', hours, weekly_punches['sun'], subtract=subtract, context=context)
        
        return
        
    def create(self, cr, uid, vals, context=None):
        
        res = super(hr_weekly_ot, self).create(cr, uid, vals, context=context)
        
        ot = self.browse(cr, uid, res, context=context)
        self.process_attendance(cr, uid, ot.id, context=context)
        
        return res
    
    def unlink(self, cr, uid, ids, context=None):
        
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        for i in ids:
            self.process_attendance(cr, uid, i, subtract=True, context=context)
        
        return super(hr_weekly_ot, self).unlink(cr, uid, ids, context=context)
    
    def write(self, cr, uid, ids, vals, context=None):
        
        if isinstance(ids, (int, long)):
            ids = [ids]
        
        for ot in self.browse(cr, uid, ids, context=None):
            weekly_punches = self.get_punch_dict(cr, uid, ot.id, context)
            
            if vals.get('mon', None) != None:
                hours = vals['mon'] == ot.mon and 0 or vals['mon'] - ot.mon
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'mon', hours,
                                            weekly_punches['mon'], subtract=(hours < 0), context=context)
            if vals.get('tue', None) != None:
                hours = vals['tue'] == ot.tue and 0 or vals['tue'] - ot.tue
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'tue', hours,
                                            weekly_punches['tue'], subtract=(hours < 0), context=context)
            if vals.get('wed', None) != None:
                hours = vals['wed'] == ot.wed and 0 or vals['wed'] - ot.wed
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'wed', hours,
                                            weekly_punches['wed'], subtract=(hours < 0), context=context)
            if vals.get('thu', None) != None:
                hours = vals['thu'] == ot.thu and 0 or vals['thu'] - ot.thu
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'thu', hours,
                                            weekly_punches['thu'], subtract=(hours < 0), context=context)
            if vals.get('fri', None) != None:
                hours = vals['fri'] == ot.fri and 0 or vals['fri'] - ot.fri
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'fri', hours,
                                            weekly_punches['fri'], subtract=(hours < 0), context=context)
            if vals.get('sat', None) != None:
                hours = vals['sat'] == ot.sat and 0 or vals['sat'] - ot.sat
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'sat', hours,
                                            weekly_punches['sat'], subtract=(hours < 0), context=context)
            if vals.get('sun', None) != None:
                hours = vals['sun'] == ot.sun and 0 or vals['sun'] - ot.sun
                if hours != 0:
                    self._modify_attendance(cr, uid, ot.employee_id, ot.weekly_id.id,
                                            ot.weekly_id.week_start, 'sun', hours,
                                            weekly_punches['sun'], subtract=(hours < 0), context=context)
        
        return super(hr_weekly_ot, self).write(cr, uid, ids, vals, context=context)

class hr_attendance(osv.osv):
    
    _name = 'hr.attendance'
    _inherit = 'hr.attendance'
    
    _columns = {
              'weekly_att_id': fields.many2one('hr.attendance.weekly', 'Weekly Attendance'),
    }

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.
        """
        for att in self.browse(cr, uid, ids, context=context):
            return True
            # search and browse for first previous and first next records
            prev_att_ids = self.search(cr, uid, [('employee_id', '=', att.employee_id.id), ('name', '<', att.name), ('action', 'in', ('sign_in', 'sign_out')), ('day','=',att.day)], limit=1, order='name DESC')
            next_add_ids = self.search(cr, uid, [('employee_id', '=', att.employee_id.id), ('name', '>', att.name), ('action', 'in', ('sign_in', 'sign_out')), ('day','=',att.day)], limit=1, order='name ASC')
            prev_atts = self.browse(cr, uid, prev_att_ids, context=context)
            next_atts = self.browse(cr, uid, next_add_ids, context=context)
            # check for alternance, return False if at least one condition is not satisfied
            if prev_atts and prev_atts[0].action == att.action: # previous exists and is same action
                return False
            if next_atts and next_atts[0].action == att.action and att.action == 'sign_out': # next exists and is same action
                return False
            if (not prev_atts) and (not next_atts) and att.action != 'sign_in': # first attendance must be sign_in
                return False
        return True

    _constraints = [(_altern_si_so, 'Error ! Sign in (resp. Sign out) must follow Sign out (resp. Sign in)', ['action'])]

class hr_employee(osv.Model):
    
    _name = 'hr.employee'
    _inherit = 'hr.employee'
    
    def _get_day_off(self, cr, uid, ids, field_name, arg, context=None):
        """Returns the index of the first rest day of the week. 0 is Monday"""
        
        sched_tpl_obj = self.pool.get('hr.schedule.template')
        
        res = dict.fromkeys(ids, '')
        for ee in self.browse(cr, uid, ids, context=context):
            if not ee.contract_id or not ee.contract_id.schedule_template_id:
                continue
            res[ee.id] = sched_tpl_obj.get_rest_days(cr, uid, ee.contract_id.schedule_template_id.id,
                                                     context=context)[0]
        
        return res
    
    _columns = {
        'rest_day': fields.function(_get_day_off, type='int', method=True, readonly=True,
                                   string="Day Off"),
    }
