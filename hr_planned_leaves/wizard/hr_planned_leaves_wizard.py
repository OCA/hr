# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
import time
import datetime
import calendar
from osv import osv, fields
from tools.translate import _

class hrself_holidays_summary_dept(osv.osv_memory):
    _name = 'hrself.holidays.summary.dept'
    _description = 'HR Holidays Summary Report By Department'
    _columns = {
        'date_from': fields.date('From', required=True),
        'date_to': fields.date('To', required=True),
        'depts': fields.many2many('hr.department', 'summary_dept_rel', 'sum_id', 'dept_id', 'Department(s)'),
        'employee_ids': fields.many2many('hr.employee', 'summary_dept_emp_rel', 'sum_id', 'emp_id', 'Employee(s)'),
#        'holiday_type': fields.selection([('Validated','Validated'),('Confirmed','Confirmed'),('both','Both Validated and Confirmed')], 'Holiday Type', required=True),
        'report_type': fields.selection([('pdf','PDF'),('excel','Excel')], 'Report Type', required=True),
        }

    def _get_depts(self, cursor, user, context={}):
        dept_id=self.pool.get('res.users').browse(cursor,user,[user],context={})[0].context_department_id.id
        return self.pool.get('hr.department').search(cursor, user, [('id', 'in' , [dept_id])])

    def _get_employee(self, cursor, user, context={}):
        dept_id=self.pool.get('res.users').browse(cursor,user,[user],context={})[0].context_department_id.id
        return self.pool.get('hr.employee').search(cursor, user, [('department_id', 'in', [dept_id])])

    def _from_date(self, cursor, user, context={}):
        return datetime.date.today().strftime('%Y-%m-01');

    def _to_date(self, cursor, user, context={}):
        today_date = datetime.date.today();
        return datetime.datetime(today_date.year, today_date.month, calendar.mdays[today_date.month]).strftime('%Y-%m-%d');

    _defaults = {
         'date_from': _from_date,
         'date_to':_to_date,
#         'holiday_type': 'Validated',
         'depts': _get_depts,
         'employee_ids': _get_employee,
         'report_type':'pdf'
        }

    def print_report(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [])[0]
        if not data['depts']:
            raise osv.except_osv(_('Error'), _('You have to select at least 1 Department. And try again'))
        datas = {
             'ids': [],
             'model': 'ir.ui.menu',
             'form': data
                 }
        return {
            'type': 'ir.actions.report.xml',
#            'report_name': 'planned.leaves',
            'report_name': 'hrself.planned.leaves',
            'datas': datas,
            'nodestroy': True,
            }

hrself_holidays_summary_dept()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: