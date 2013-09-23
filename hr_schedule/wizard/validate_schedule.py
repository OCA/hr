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

import netsvc

from osv import fields, osv

import logging
_logger = logging.getLogger(__name__)


class department_selection(osv.osv_memory):

    _name = 'hr.schedule.validate.departments'
    _description = 'Department Selection for Validation'

    _columns = {
        'department_ids': fields.many2many('hr.department', 'hr_department_group_rel', 'employee_id', 'department_id', 'Departments'),
    }

    def view_schedules(self, cr, uid, ids, context=None):

        data = self.read(cr, uid, ids, context=context)[0]
        return {
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.schedule',
            'domain': [('department_id', 'in', data['department_ids']), ('state', 'in', ['draft'])],
            'type': 'ir.actions.act_window',
            'target': 'new',
            'nodestroy': True,
            'context': context,
        }

    def do_validate(self, cr, uid, ids, context=None):

        wkf_service = netsvc.LocalService('workflow')
        data = self.read(cr, uid, ids, context=context)[0]
        sched_ids = self.pool.get('hr.schedule').search(cr, uid,
                                                        [('department_id', 'in', data[
                                                          'department_ids'])],
                                                        context=context)
        for sched_id in sched_ids:
            wkf_service.trg_validate(
                uid, 'hr.schedule', sched_id, 'signal_validate', cr)

        return {'type': 'ir.actions.act_window_close'}
