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

from openerp.osv import fields, osv

from hr_employee_education.hr import EDUCATION_SELECTION

import logging
_l = logging.getLogger(__name__)

class hr_al(osv.TransientModel):
    
    _name = 'hr.employee.edu'
    
    _columns = {
        'department_id': fields.many2one('hr.department', 'Department'),
        'line_ids': fields.one2many('hr.employee.edu.line', 'edu_id', 'Employee Education Lines'),
    }
    

    def _get_lines(self, cr, uid, context=None):
        
        if context == None:
            context= {}
        
        res = []
        ee_obj = self.pool.get('hr.employee')
        department_id = context.get('active_id', False)
        ee_ids = ee_obj.search(cr, uid, [('department_id', '=', department_id),
                                         ('active', '=', True)], context=context)
        data = ee_obj.read(cr, uid, ee_ids, ['education'], context=context)
        for record in data:
            vals = {
                    'employee_id': record['id'],
                    'days': record['education'],
            }
                
            res.append(vals)
        return res
    
    def _get_department(self, cr, uid, context=None):
        
        if context == None:
            context= {}
        department_id = context.get('active_id', False)
        return  department_id
    
    _defaults = {
        'department_id': _get_department,
        'line_ids': _get_lines,
    }
    
    def add_records(self, cr, uid, ids, context=None):
        
        e_obj = self.pool.get('hr.employee')
        data = self.read(cr, uid, ids[0], ['line_ids'], context=context)
        for line in self.pool.get('hr.employee.edu.line').browse(cr, uid, data['line_ids'],
                                                                context=context):
            if line.education:
                e_obj.write(cr, uid, line.employee_id.id, {'education': line.education},
                            context=context)
        
        return {'type': 'ir.actions.act_window_close'}

class hr_edu_line(osv.TransientModel):
    
    _name = 'hr.employee.edu.line'
    
    _columns = {
        'edu_id': fields.many2one('hr.employee.edu', 'Education by Dept.'),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True),
        'education': fields.selection(EDUCATION_SELECTION, 'Education'),
    }
