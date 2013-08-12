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

from datetime import datetime, timedelta
from pytz import timezone

from osv import fields, osv
import logging
_logger = logging.getLogger(__name__)

class payroll_register_run(osv.osv_memory):
    
    _name = 'hr.payroll.register.run'
    _description = 'Pay Slip Creation'
    
    _columns = {
                'department_ids': fields.many2many('hr.department',
                                                   'hr_department_payslip_run_rel',
                                                   'register_id', 'register_run_id',
                                                   'Departments'),
    }
    
    def create_payslip_runs(self, cr, uid, ids, context=None):
        dept_pool = self.pool.get('hr.department')
        ee_pool = self.pool.get('hr.employee')
        slip_pool = self.pool.get('hr.payslip')
        run_pool = self.pool.get('hr.payslip.run')
        reg_pool = self.pool.get('hr.payroll.register')
        if context is None:
            context = {}
        data = self.read(cr, uid, ids, context=context)[0]
        register_id = context.get('active_id', False)
        if not register_id:
            raise osv.except_osv(_("Programming Error !"), _("Unable to determine Payroll Register Id."))
        
        if not data['department_ids']:
            raise osv.except_osv(_("Warning !"), _("No departments selected for payslip generation."))

        pr = reg_pool.browse(cr, uid, register_id, context=context)
        
        # DateTime in db is store as naive UTC. Convert it to explicit UTC and then convert
        # that into the our time zone.
        #
        user_data = self.pool.get('res.users').read(cr, uid, uid, ['tz'], context=context)
        local_tz = timezone(user_data['tz'])
        utc_tz = timezone('UTC')
        utcDTStart = utc_tz.localize(datetime.strptime(pr.date_start, '%Y-%m-%d %H:%M:%S'))
        loclDTStart = utcDTStart.astimezone(local_tz)
        date_start = loclDTStart.strftime('%Y-%m-%d')
        utcDTEnd = utc_tz.localize(datetime.strptime(pr.date_end, '%Y-%m-%d %H:%M:%S'))
        loclDTEnd = utcDTEnd.astimezone(local_tz)
        date_end = loclDTEnd.strftime('%Y-%m-%d')

        for dept in dept_pool.browse(cr, uid, data['department_ids'], context=context):
            run_res = {
                'name': dept.complete_name,
                'date_start': pr.date_start,
                'date_end': pr.date_end,
                'register_id': register_id,
            }
            run_id = run_pool.create(cr, uid, run_res, context=context)
            
            slip_ids = []
            ee_ids = ee_pool.search(cr, uid, [('department_id','=',dept.id)], order="name", context=context)
            for ee in ee_pool.browse(cr, uid, ee_ids, context=context):
                slip_data = slip_pool.onchange_employee_id(cr, uid, [],
                                                           date_start, date_end,
                                                           ee.id, contract_id=False,
                                                           context=context)
                res = {
                    'employee_id': ee.id,
                    'name': slip_data['value'].get('name', False),
                    'struct_id': slip_data['value'].get('struct_id', False),
                    'contract_id': slip_data['value'].get('contract_id', False),
                    'payslip_run_id': run_id,
                    'input_line_ids': [(0, 0, x) for x in slip_data['value'].get('input_line_ids', False)],
                    'worked_days_line_ids': [(0, 0, x) for x in slip_data['value'].get('worked_days_line_ids', False)],
                    'date_from': pr.date_start,
                    'date_to': pr.date_end,
                }
                slip_ids.append(slip_pool.create(cr, uid, res, context=context))
            slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        
        return {'type': 'ir.actions.act_window_close'}
