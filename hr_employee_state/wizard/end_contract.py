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

import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class employee_set_inactive(osv.TransientModel):

    _name = 'hr.contract.end'
    _description = 'Employee De-Activation Wizard'

    _columns = {
        'contract_id': fields.many2one('hr.contract', 'Contract', readonly=True),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=True),
        'date': fields.date('Date', required=True),
        'reason_id': fields.many2one('hr.employee.termination.reason', 'Reason', required=True),
        'notes': fields.text('Notes'),
    }

    def _get_contract(self, cr, uid, context=None):

        if context == None:
            context = {}

        return context.get('end_contract_id', False)

    def _get_employee(self, cr, uid, context=None):

        if context == None:
            context = {}

        contract_id = context.get('end_contract_id', False)
        if not contract_id:
            return False

        data = self.pool.get(
            'hr.contract').read(cr, uid, contract_id, ['employee_id'],
                                context=context)
        return data['employee_id'][0]

    _defaults = {
        'date': datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT),
        'employee_id': _get_employee,
        'contract_id': _get_contract,
    }

    def set_employee_inactive(self, cr, uid, ids, context=None):

        data = self.read(
            cr, uid, ids[0], [
                'employee_id', 'contract_id', 'date', 'reason_id', 'notes'],
            context=context)
        vals = {
            'name': data['date'],
            'employee_id': data['employee_id'][0],
            'reason_id': data['reason_id'][0],
            'notes': data['notes'],
        }

        contract_obj = self.pool.get('hr.contract')
        contract = contract_obj.browse(
            cr, uid, data['contract_id'][0], context=context)
        contract_obj.setup_pending_done(
            cr, uid, contract, vals, context=context)

        return {'type': 'ir.actions.act_window_close'}
