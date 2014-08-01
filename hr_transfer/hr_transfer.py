# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
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

from openerp import netsvc
from openerp.osv import fields, orm
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class hr_transfer(orm.Model):

    _name = 'hr.department.transfer'
    _description = 'Departmental Transfer'

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=True,
                                       states={
                                           'draft': [('readonly', False)]}),
        'src_id': fields.many2one('hr.job', 'From', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}),
        'dst_id': fields.many2one('hr.job', 'Destination', required=True, readonly=True,
                                  states={'draft': [('readonly', False)]}),
        'src_department_id': fields.related('src_id', 'department_id', type='many2one',
                                            relation='hr.department', string='From Department',
                                            store=True, readonly=True),
        'dst_department_id': fields.related('dst_id', 'department_id', type='many2one',
                                            relation='hr.department', store=True,
                                            string='Destination Department', readonly=True),
        'src_contract_id': fields.many2one('hr.contract', 'From Contract', readonly=True,
                                           states={
                                               'draft': [('readonly', False)]}),
        'dst_contract_id': fields.many2one('hr.contract', 'Destination Contract', readonly=True),
        'date': fields.date('Effective Date', required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('pending', 'Pending'),
            ('done', 'Done'),
            ('cancel', 'Cancelled'),
        ],
            'State', readonly=True),
    }

    _rec_name = 'date'

    _defaults = {
        'state': 'draft',
    }

    _track = {
        'state': {
            'hr_transfer.mt_alert_xfer_confirmed': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_transfer.mt_alert_xfer_pending': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'pending',
            'hr_transfer.mt_alert_xfer_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
        },
    }

    def _needaction_domain_get(self, cr, uid, context=None):

        users_obj = self.pool.get('res.users')

        if users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            domain = [('state', '=', 'confirm')]
            return domain

        return False

    def unlink(self, cr, uid, ids, context=None):

        for xfer in self.browse(cr, uid, ids, context=context):
            if xfer.state not in ['draft']:
                raise orm.except_orm(
                    _('Unable to Delete Transfer!'),
                    _('Transfer has been initiated. Either cancel the transfer or create another transfer to undo it.')
                )

        return super(hr_transfer, self).unlink(cr, uid, ids, context=context)

    def onchange_employee(self, cr, uid, ids, employee_id, context=None):

        res = {'value': {'src_id': False, 'src_contract_id': False}}

        if employee_id:
            ee = self.pool.get('hr.employee').browse(
                cr, uid, employee_id, context=context)
            res['value']['src_id'] = ee.contract_id.job_id.id
            res['value']['src_contract_id'] = ee.contract_id.id

        return res

    def effective_date_in_future(self, cr, uid, ids, context=None):

        today = datetime.now().date()
        for xfer in self.browse(cr, uid, ids, context=context):
            effective_date = datetime.strptime(
                xfer.date, DEFAULT_SERVER_DATE_FORMAT).date()
            if effective_date <= today:
                return False

        return True

    def _check_state(self, cr, uid, contract_id, effective_date, context=None):

        contract_obj = self.pool.get('hr.contract')
        data = contract_obj.read(
            cr, uid, contract_id, ['state', 'date_end'], context=context)

        if data['state'] not in ['trial', 'trial_ending', 'open', 'contract_ending']:
            raise orm.except_orm(
                _('Warning!'),
                _('The current state of the contract does not permit changes.')
            )

        if data.get('date_end', False) and data['date_end'] != '':
            dContractEnd = datetime.strptime(
                data['date_end'], DEFAULT_SERVER_DATE_FORMAT)
            dEffective = datetime.strptime(
                effective_date, DEFAULT_SERVER_DATE_FORMAT)
            if dEffective >= dContractEnd:
                raise orm.except_orm(
                    _('Warning!'),
                    _('The contract end date is on or before the effective date of the transfer.')
                )

        return True

    def transfer_contract(self, cr, uid, contract_id, job_id, xfer_id, effective_date, context=None):

        contract_obj = self.pool.get('hr.contract')

        # Copy the contract and adjust start/end dates, job id, etc. accordingly.
        #
        default = {
            'job_id': job_id,
            'date_start': effective_date,
            'name': False,
            'state': False,
            'message_ids': False,
            'trial_date_start': False,
            'trial_date_end': False,
        }
        data = contract_obj.copy_data(
            cr, uid, contract_id, default=default, context=context)

        c_id = contract_obj.create(cr, uid, data, context=context)
        if c_id:
            vals = {}
            wkf = netsvc.LocalService('workflow')

            # Set the new contract to the appropriate state
            wkf.trg_validate(uid, 'hr.contract', c_id, 'signal_confirm', cr)

            # Terminate the current contract (and trigger appropriate state
            # change)
            vals['date_end'] = datetime.strptime(
                effective_date, '%Y-%m-%d').date() + relativedelta(days=-1)
            contract_obj.write(cr, uid, contract_id, vals, context=context)
            wkf.trg_validate(
                uid, 'hr.contract', contract_id, 'signal_done', cr)

            # Link to the new contract
            self.pool.get(
                'hr.department.transfer').write(cr, uid, xfer_id, {'dst_contract_id': c_id},
                                                context=context)

        return

    def state_confirm(self, cr, uid, ids, context=None):

        for xfer in self.browse(cr, uid, ids, context=context):
            self._check_state(
                cr, uid, xfer.src_contract_id.id, xfer.date, context=context)
            self.write(cr, uid, xfer.id, {'state': 'confirm'}, context=context)

        return True

    def state_done(self, cr, uid, ids, context=None):

        employee_obj = self.pool.get('hr.employee')
        today = datetime.now().date()

        for xfer in self.browse(cr, uid, ids, context=context):
            if datetime.strptime(xfer.date, DEFAULT_SERVER_DATE_FORMAT).date() <= today:
                self._check_state(
                    cr, uid, xfer.src_contract_id.id, xfer.date, context=context)
                employee_obj.write(
                    cr, uid, xfer.employee_id.id, {
                        'department_id': xfer.dst_department_id.id},
                    context=context)
                self.transfer_contract(
                    cr, uid, xfer.src_contract_id.id, xfer.dst_id.id,
                    xfer.id, xfer.date, context=context)
                self.write(
                    cr, uid, xfer.id, {'state': 'done'}, context=context)
            else:
                return False

        return True

    def try_pending_department_transfers(self, cr, uid, context=None):
        """Completes pending departmental transfers. Called from the scheduler."""

        xfer_obj = self.pool.get('hr.department.transfer')
        today = datetime.now().date()
        xfer_ids = xfer_obj.search(cr, uid, [
            ('state', '=', 'pending'),
            ('date', '<=', today.strftime(
                DEFAULT_SERVER_DATE_FORMAT)),
        ], context=context)

        wkf = netsvc.LocalService('workflow')
        [wkf.trg_validate(uid, 'hr.department.transfer', xfer.id, 'signal_done', cr)
         for xfer in self.browse(cr, uid, xfer_ids, context=context)]

        return True
