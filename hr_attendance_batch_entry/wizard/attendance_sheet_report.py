#-*- coding:utf-8 -*-
##############################################################################
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
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta

from osv import fields, osv

class print_attendance_sheet(osv.TransientModel):
    
    _name = 'hr.attendance.sheet'
    _description = 'Attendance Sheet Wizard'
    
    _columns = {
        'week_start': fields.date('Start of Week', required=True),
        'department_ids': fields.many2many('hr.department', 'print_attendance_by_dept_rel',
                                           'department_id', 'attendance_sheet_id', 'Departments'),
    }
    
    _defaults = {
        'week_start': str(datetime.now().date() + relativedelta(days= +(7 - datetime.now().date().weekday())))[:10],
    }
    
    def onchange_week_start(self, cr, uid, ids, newdate):
        
        res = {'value': {'week_start': newdate}}
        if newdate:
            d = datetime.strptime(newdate, "%Y-%m-%d")
            if d.weekday() != 0:
                res['value']['week_start'] = False
                return res
        return res

    def print_report(self, cr, uid, ids, context=None):
        form = self.read(cr, uid, ids, [], context=context)[0]
        form['week_no'] = datetime.strptime(form['week_start'], '%Y-%m-%d').isocalendar()[1]
        
        department_ids = []
        dep_obj = self.pool.get('hr.department')
        for dep in dep_obj.browse(cr, uid, form['department_ids'], context=context):
            # Add not only selected departments, but also their descendants as well
            more_ids = dep_obj.search(cr, uid, [('id', 'child_of', dep.id)], context=context)
            for m in dep_obj.browse(cr, uid, more_ids, context=context):
                if len(m.member_ids) > 0 and m.id not in department_ids:
                    department_ids.append(m.id)
            
            if len(dep.member_ids) == 0:
                continue
            
            if dep.id not in department_ids:
                department_ids.append(dep.id)
        
        datas = {
             'ids': department_ids,
             'model': 'hr.department',
             'form': form
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'attendance_sheet_report',
            'datas': datas,
        }
