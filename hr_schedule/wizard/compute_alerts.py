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

from datetime import datetime
from dateutil.relativedelta import relativedelta

from openerp.osv import fields, osv


class compute_alerts(osv.TransientModel):

    _name = 'hr.schedule.alert.compute'
    _description = 'Check Alerts'

    _columns = {
        'date_start': fields.date('Start', required=True),
        'date_end': fields.date('End', required=True),
        'employee_ids': fields.many2many('hr.employee', 'hr_employee_alert_rel',
                                         'generate_id', 'employee_id', 'Employees'),
    }

    def generate_alerts(self, cr, uid, ids, context=None):

        alert_obj = self.pool.get('hr.schedule.alert')

        data = self.read(cr, uid, ids, context=context)[0]
        dStart = datetime.strptime(data['date_start'], '%Y-%m-%d').date()
        dEnd = datetime.strptime(data['date_end'], '%Y-%m-%d').date()
        dToday = datetime.strptime(fields.date.context_today(
            self, cr, uid, context=context), '%Y-%m-%d').date()
        if dToday < dEnd:
            dEnd = dToday

        dNext = dStart
        for employee_id in data['employee_ids']:
            while dNext <= dEnd:
                alert_obj.compute_alerts_by_employee(cr, uid, employee_id,
                                                     dNext.strftime(
                                                         '%Y-%m-%d'),
                                                     context=context)
                dNext += relativedelta(days=+1)

        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.schedule.alert',
            'domain': [('employee_id', 'in', data['employee_ids']), '&', ('name', '>=', data['date_start'] + ' 00:00:00'), ('name', '<=', data['date_end'] + ' 23:59:59')],
            'type': 'ir.actions.act_window',
            'target': 'current',
            'nodestroy': True,
            'context': context,
        }
