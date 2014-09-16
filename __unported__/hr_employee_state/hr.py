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

import time

from datetime import datetime

from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


class hr_employee(osv.Model):

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    _columns = {
        # 'state' is already being used by hr_attendance
        'status': fields.selection([
            ('new', 'New-Hire'),
            ('onboarding', 'On-Boarding'),
            ('active', 'Active'),
            ('pending_inactive', 'Pending Deactivation'),
            ('inactive', 'Inactive'),
            ('reactivated', 'Re-Activated'),
        ],
            'Status', readonly=True),
        'inactive_ids': fields.one2many('hr.employee.termination', 'employee_id', 'Deactivation Records'),
        'saved_department_id': fields.many2one('hr.department', 'Saved Department'),
    }

    _defaults = {
        'status': 'new',
    }

    def condition_finished_onboarding(self, cr, uid, ids, context=None):

        employee = self.browse(cr, uid, ids[0], context=context)
        if employee.status == 'onboarding':
            return True

        return False

    def state_active(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        data = self.read(
            cr, uid, ids, ['status', 'saved_department_id'], context=context)
        for d in data:
            if d['status'] and d['status'] == 'pending_inactive':
                self.write(cr, uid, d['id'],
                           {'status': 'active',
                            'department_id': d['saved_department_id'] and d['saved_department_id'][0] or False,
                            'saved_department_id': False},
                           context=context)
            else:
                self.write(cr, uid, ids, {'status': 'active'}, context=context)

        return True

    def state_pending_inactive(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        data = self.read(cr, uid, ids, ['department_id'], context=context)
        for d in data:
            self.write(cr, uid, d['id'],
                       {'status': 'pending_inactive',
                        'saved_department_id': d['department_id'] and d['department_id'][0] or False,
                        'department_id': False},
                       context=context)

        return True

    def state_inactive(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        data = self.read(
            cr, uid, ids, ['status', 'saved_department_id'], context=context)
        for d in data:
            vals = {
                'active': False,
                'status': 'inactive',
                'job_id': False,
            }
            if d['status'] and d['status'] == 'pending_inactive':
                vals.update(
                    {'department_id': d['saved_department_id'] and d['saved_department_id'][0] or False,
                     'saved_department_id': False})

            self.pool.get('hr.employee').write(
                cr, uid, d['id'], vals, context=context)

        return True

    def signal_reactivate(self, cr, uid, ids, context=None):

        for employee in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, employee.id, {'active': True}, context=context)
            netsvc.LocalService('workflow').trg_validate(
                uid, 'hr.employee', employee.id, 'signal_reactivate', cr)

        return True


class hr_employee_termination_reason(osv.Model):

    _name = 'hr.employee.termination.reason'
    _description = 'Reason for Employment Termination'

    _columns = {
        'name': fields.char('Name', size=256, required=True),
    }


class hr_employee_termination(osv.osv):

    _name = 'hr.employee.termination'
    _description = 'Data Related to Deactivation of Employee'

    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _columns = {
        'name': fields.date('Effective Date', required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'reason_id': fields.many2one('hr.employee.termination.reason', 'Reason', required=True,
                                     readonly=True, states={
                                         'draft': [('readonly', False)]}),
        'notes': fields.text('Notes', readonly=True, states={'draft': [('readonly', False)]}),
        'employee_id': fields.many2one('hr.employee', 'Employee', required=True, readonly=True),
        'department_id': fields.related('employee_id', 'department_id', type='many2one',
                                        relation='hr.department', store=True, string="Department"),
        'saved_department_id': fields.related('employee_id', 'saved_department_id', type='many2one',
                                              relation='hr.department', store=True, string="Department"),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('cancel', 'Cancelled'),
            ('done', 'Done'),
        ],
            'State', readonly=True),
    }

    _defaults = {
        'state': 'draft',
    }

    _track = {
        'state': {
            'hr_employee_state.mt_alert_state_confirm': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'confirm',
            'hr_employee_state.mt_alert_state_done': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'done',
            'hr_employee_state.mt_alert_state_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    def _needaction_domain_get(self, cr, uid, context=None):

        users_obj = self.pool.get('res.users')
        domain = []

        if users_obj.has_group(cr, uid, 'base.group_hr_user'):
            domain = [('state', 'in', ['draft'])]

        if users_obj.has_group(cr, uid, 'base.group_hr_manager'):
            if len(domain) > 0:
                domain = ['|'] + domain + [('state', '=', 'confirm')]
            else:
                domain = [('state', '=', 'confirm')]

        if len(domain) > 0:
            return domain

        return False

    def unlink(self, cr, uid, ids, context=None):

        for term in self.browse(cr, uid, ids, context=context):
            if term.state not in ['draft']:
                raise osv.except_osv(_('Unable to delete record!'),
                                     _('Employment termination already in progress. Use the "Cancel" button instead.'))

            # Trigger employee status change back to Active and contract back
            # to Open
            wkf = netsvc.LocalService('workflow')
            wkf.trg_validate(
                uid, 'hr.employee', term.employee_id.id, 'signal_active', cr)
            for contract in term.employee_id.contract_ids:
                if contract.state == 'pending_done':
                    wkf.trg_validate(
                        uid, 'hr.contract', contract.id, 'signal_open', cr)

        return super(hr_employee_termination, self).unlink(cr, uid, ids, context=context)

    def effective_date_in_future(self, cr, uid, ids, context=None):

        today = datetime.now().date()
        for term in self.browse(cr, uid, ids, context=context):
            effective_date = datetime.strptime(
                term.name, DEFAULT_SERVER_DATE_FORMAT).date()
            if effective_date <= today:
                return False

        return True

    def state_cancel(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        for term in self.browse(cr, uid, ids, context=context):

            # Trigger a status change of the employee and his contract(s)
            wkf = netsvc.LocalService('workflow')
            wkf.trg_validate(
                uid, 'hr.employee', term.employee_id.id, 'signal_active', cr)
            for contract in term.employee_id.contract_ids:
                if contract.state == 'pending_done':
                    wkf.trg_validate(
                        uid, 'hr.contract', contract.id, 'signal_open', cr)

            self.write(cr, uid, term.id, {'state': 'cancel'}, context=context)

        return True

    def state_done(self, cr, uid, ids, context=None):

        for term in self.browse(cr, uid, ids, context=context):
            if self.effective_date_in_future(cr, uid, [term.id], context=context):
                raise osv.except_osv(_('Unable to deactivate employee!'),
                                     _('Effective date is still in the future.'))

            # Trigger a status change of the employee and any contracts pending
            # termination.
            wkf = netsvc.LocalService('workflow')
            for contract in term.employee_id.contract_ids:
                if contract.state == 'pending_done':
                    wkf.trg_validate(
                        uid, 'hr.contract', contract.id, 'signal_done', cr)
            wkf.trg_validate(
                uid, 'hr.employee', term.employee_id.id, 'signal_inactive', cr)

            self.write(cr, uid, term.id, {'state': 'done'}, context=context)

        return True


class hr_contract(osv.Model):

    _name = 'hr.contract'
    _inherit = 'hr.contract'

    def end_contract(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]

        if len(ids) == 0:
            return False

        context.update({'end_contract_id': ids[0]})
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.contract.end',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context
        }

    def _state_common(self, cr, uid, ids, context=None):

        wkf = netsvc.LocalService('workflow')
        for contract in self.browse(cr, uid, ids, context=context):
            if contract.employee_id.status == 'new':
                wkf.trg_validate(
                    uid, 'hr.employee', contract.employee_id.id, 'signal_confirm', cr)

    def state_trial(self, cr, uid, ids, context=None):
        """Override 'trial' contract state to also change employee state: new -> onboarding"""

        res = super(hr_contract, self).state_trial(
            cr, uid, ids, context=context)
        self._state_common(cr, uid, ids, context=context)
        return res

    def state_open(self, cr, uid, ids, context=None):
        """Override 'open' contract state to also change employee state: new -> onboarding"""

        res = super(hr_contract, self).state_open(
            cr, uid, ids, context=context)
        self._state_common(cr, uid, ids, context=context)
        return res

    def try_signal_contract_completed(self, cr, uid, context=None):

        d = datetime.now().date()
        ids = self.search(cr, uid, [
            ('state', '=', 'open'),
            ('date_end', '<', d.strftime(
                DEFAULT_SERVER_DATE_FORMAT))
        ], context=context)
        if len(ids) == 0:
            return

        for c in self.browse(cr, uid, ids, context=context):
            vals = {
                'name': c.date_end and c.date_end or time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                'employee_id': c.employee_id.id,
                'reason': 'contract_end',
            }
            self.setup_pending_done(cr, uid, c, vals, context=context)

        return

    def setup_pending_done(self, cr, uid, contract, term_vals, context=None):
        """Start employee deactivation process."""

        term_obj = self.pool.get('hr.employee.termination')
        dToday = datetime.now().date()

        # If employee is already inactive simply end the contract
        wkf = netsvc.LocalService('workflow')
        if not contract.employee_id.active:
            wkf.trg_validate(
                uid, 'hr.contract', contract.id, 'signal_done', cr)
            return

        # Ensure there are not other open contracts
        #
        open_contract = False
        ee = self.pool.get('hr.employee').browse(
            cr, uid, contract.employee_id.id, context=context)
        for c2 in ee.contract_ids:
            if c2.id == contract.id or c2.state == 'draft':
                continue

            if (not c2.date_end or datetime.strptime(c2.date_end, DEFAULT_SERVER_DATE_FORMAT).date() >= dToday) and c2.state != 'done':
                open_contract = True

        # Don't create an employment termination if the employee has an open contract or
        # if this contract is already in the 'done' state.
        if open_contract or contract.state == 'done':
            return

        # Also skip creating an employment termination if there is already one in
        # progress for this employee.
        #
        term_ids = term_obj.search(
            cr, uid, [('employee_id', '=', contract.employee_id.id),
                      ('state', 'in', ['draft', 'confirm'])],
            context=context)
        if len(term_ids) > 0:
            return

        term_obj.create(cr, uid, term_vals, context=context)

        # Set the contract state to pending completion
        wkf = netsvc.LocalService('workflow')
        wkf.trg_validate(
            uid, 'hr.contract', contract.id, 'signal_pending_done', cr)

        # Set employee state to pending deactivation
        wkf.trg_validate(
            uid, 'hr.employee', contract.employee_id.id, 'signal_pending_inactive', cr)


class hr_job(osv.Model):

    _name = 'hr.job'
    _inherit = 'hr.job'

    # Override calculation of number of employees in job. Remove employees for
    # which the termination process has already started.
    #
    def _no_of_employee(self, cr, uid, ids, name, args, context=None):
        res = {}
        count = 0
        for job in self.browse(cr, uid, ids, context=context):
            for ee in job.employee_ids:
                if ee.active and ee.status not in ['pending_inactive']:
                    count += 1

            res[job.id] = {
                'no_of_employee': count,
                'expected_employees': count + job.no_of_recruitment,
            }
        return res

    def _get_job_position(self, cr, uid, ids, context=None):
        res = []
        data = self.pool.get('hr.employee').read(
            cr, uid, ids, ['job_id'], context=context)
        [res.append(d['job_id'][0]) for d in data if d['job_id']]
        return res

    _columns = {
        # Override from base class. Also, watch 'status' field of hr.employee
        'no_of_employee': fields.function(_no_of_employee, string="Current Number of Employees",
                                          help='Number of employees currently occupying this job position.',
                                          store={
                                              'hr.employee': (_get_job_position, ['job_id', 'status'], 10),
                                          },
                                          multi='no_of_employee'),
        'expected_employees': fields.function(_no_of_employee, string='Total Forecasted Employees',
                                              help='Expected number of employees for this job position after new recruitment.',
                                              store={
                                                  'hr.job': (lambda self, cr, uid, ids, c=None: ids, ['no_of_recruitment'], 10),
                                                  'hr.employee': (_get_job_position, ['job_id', 'status'], 10),
                                              },
                                              multi='no_of_employee'),
    }
