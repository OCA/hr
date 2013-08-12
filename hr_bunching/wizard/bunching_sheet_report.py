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
    
    _name = 'hr.bunching.sheet.report'
    _description = 'Attendance Sheet Wizard'
    
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        'employee_ids': fields.many2many('hr.employee', 'report_bunching_by_emp_rel', 'report_id',
                                         'employee_id', 'Employees'),
    }
    
    def onchange_department(self, cr, uid, ids, department_id, context=None):
        
        dep_obj = self.pool.get('hr.department')
        dep = dep_obj.browse(cr, uid, department_id, context=context)
        res = {'value': {'employee_ids': []}}
        
        if not department_id:
            return res
        
        employee_ids = []
        department_ids = []
        # Add not only selected departments, but also their descendants as well
        more_ids = dep_obj.search(cr, uid, [('id', 'child_of', dep.id)], context=context)
        for d in dep_obj.browse(cr, uid, more_ids, context=context):
            if len(d.member_ids) > 0 and d.id not in department_ids:
                [employee_ids.append(ee.id) for ee in d.member_ids if ee.id not in employee_ids]
                department_ids.append(d.id)
        
        if len(dep.member_ids) > 0 and dep.id not in department_ids:
            [employee_ids.append(m.id) for m in dep.member_ids if m.id not in employee_ids]
            department_ids.append(dep.id)
        
        res['value']['employee_ids'] += employee_ids
        return res

    def print_report(self, cr, uid, ids, context=None):
        form = self.read(cr, uid, ids, [], context=context)[0]
        datas = {
             'ids': form['employee_ids'],
             'model': 'hr.employee',
             'form': form
        }
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'hr_bunching_sheet',
            'datas': datas,
        }
