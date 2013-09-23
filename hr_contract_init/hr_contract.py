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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from openerp import netsvc
from openerp.addons import decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as OE_DFORMAT
from openerp.tools.translate import _


class contract_init(osv.Model):

    _name = 'hr.contract.init'
    _description = 'Initial Contract Settings'

    _inherit = 'ir.needaction_mixin'

    _columns = {
        'name': fields.char('Name', size=64, required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'date': fields.date('Effective Date', required=True, readonly=True,
                            states={'draft': [('readonly', False)]}),
        'wage_ids': fields.one2many('hr.contract.init.wage', 'contract_init_id',
                                    'Starting Wages', readonly=True,
                                    states={'draft': [('readonly', False)]}),
        'struct_id': fields.many2one('hr.payroll.structure', 'Payroll Structure', readonly=True,
                                     states={'draft': [('readonly', False)]}),
        'trial_period': fields.integer('Trial Period', readonly=True,
                                       states={'draft': [('readonly', False)]},
                                       help="Length of Trial Period, in days"),
        'active': fields.boolean('Active'),
        'state': fields.selection([('draft', 'Draft'),
                                   ('approve', 'Approved'),
                                   ('decline', 'Declined')], 'State', readonly=True),
    }

    _defaults = {
        'trial_period': 0,
        'active': True,
        'state': 'draft',
    }

    # Return records with latest date first
    _order = 'date desc'

    def _needaction_domain_get(self, cr, uid, context=None):

        users_obj = self.pool.get('res.users')
        domain = []

        if users_obj.has_group(cr, uid, 'base.group_hr_director'):
            domain = [('state', 'in', ['draft'])]
            return domain

        return False

    def unlink(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]
        data = self.read(cr, uid, ids, ['state'], context=context)
        for d in data:
            if d['state'] in ['approve', 'decline']:
                raise osv.except_osv(_('Error'),
                                     _('You may not a delete a record that is not in a "Draft" state'))
        return super(contract_init, self).unlink(cr, uid, ids, context=context)

    def set_to_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {
            'state': 'draft',
        })
        wf_service = netsvc.LocalService("workflow")
        for i in ids:
            wf_service.trg_delete(uid, 'hr.contract.init', i, cr)
            wf_service.trg_create(uid, 'hr.contract.init', i, cr)
        return True

    def state_approve(self, cr, uid, ids, context=None):

        self.write(cr, uid, ids, {'state': 'approve'}, context=context)
        return True

    def state_decline(self, cr, uid, ids, context=None):

        self.write(cr, uid, ids, {'state': 'decline'}, context=context)
        return True


class init_wage(osv.Model):

    _name = 'hr.contract.init.wage'
    _description = 'Starting Wages'

    _columns = {
        'job_id': fields.many2one('hr.job', 'Job'),
        'starting_wage': fields.float('Starting Wage', digits_compute=dp.get_precision('Payroll'),
                                      required=True),
        'is_default': fields.boolean('Use as Default',
                                     help="Use as default wage"),
        'contract_init_id': fields.many2one('hr.contract.init', 'Contract Settings'),
        'category_ids': fields.many2many('hr.employee.category', 'contract_init_category_rel', 'contract_init_id', 'category_id', 'Tags'),
    }

    _sql_constraints = [('unique_job_cinit', 'UNIQUE(job_id,contract_init_id)', _(
        'A Job Position cannot be referenced more than once in a Contract Settings record.'))]

    def unlink(self, cr, uid, ids, context=None):

        if isinstance(ids, (int, long)):
            ids = [ids]
        data = self.read(cr, uid, ids, ['contract_init_id'], context=context)
        for d in data:
            if not d.get('contract_init_id', False):
                continue
            d2 = self.pool.get(
                'hr.contract.init').read(cr, uid, d['contract_init_id'][0],
                                         ['state'], context=context)
            if d2['state'] in ['approve', 'decline']:
                raise osv.except_osv(_('Error'),
                                     _('You may not a delete a record that is not in a "Draft" state'))
        return super(init_wage, self).unlink(cr, uid, ids, context=context)


class hr_contract(osv.Model):

    _inherit = 'hr.contract'

    def _get_wage(self, cr, uid, context=None, job_id=None):

        res = 0
        default = 0
        init = self.get_latest_initial_values(cr, uid, context=context)
        if job_id:
            catdata = self.pool.get('hr.job').read(
                cr, uid, job_id, ['category_ids'], context=context)
        else:
            catdata = False
        if init != None:
            for line in init.wage_ids:
                if job_id != None and line.job_id.id == job_id:
                    res = line.starting_wage
                elif catdata:
                    cat_id = False
                    category_ids = [c.id for c in line.category_ids]
                    for ci in catdata['category_ids']:
                        if ci in category_ids:
                            cat_id = ci
                            break
                    if cat_id:
                        res = line.starting_wage
                if line.is_default and default == 0:
                    default = line.starting_wage
                if res != 0:
                    break
        if res == 0:
            res = default
        return res

    def _get_struct(self, cr, uid, context=None):

        res = False
        init = self.get_latest_initial_values(cr, uid, context=context)
        if init != None and init.struct_id:
            res = init.struct_id.id
        return res

    def _get_trial_date_start(self, cr, uid, context=None):

        res = False
        init = self.get_latest_initial_values(cr, uid, context=context)
        if init != None and init.trial_period and init.trial_period > 0:
            res = datetime.now().strftime(OE_DFORMAT)
        return res

    def _get_trial_date_end(self, cr, uid, context=None):

        res = False
        init = self.get_latest_initial_values(cr, uid, context=context)
        if init != None and init.trial_period and init.trial_period > 0:
            dEnd = datetime.now().date() + timedelta(days=init.trial_period)
            res = dEnd.strftime(OE_DFORMAT)
        return res

    _defaults = {
        'wage': _get_wage,
        'struct_id': _get_struct,
        'trial_date_start': _get_trial_date_start,
        'trial_date_end': _get_trial_date_end,
    }

    def onchange_job(self, cr, uid, ids, job_id, context=None):

        res = False
        if job_id:
            wage = self._get_wage(cr, uid, context=context, job_id=job_id)
            res = {'value': {'wage': wage}}
        return res

    def onchange_trial(self, cr, uid, ids, trial_date_start, context=None):

        res = {'value': {'trial_date_end': False}}

        init = self.get_latest_initial_values(cr, uid, context=context)
        if init != None and init.trial_period and init.trial_period > 0:
            dStart = datetime.strptime(trial_date_start, OE_DFORMAT)
            dEnd = dStart + timedelta(days=init.trial_period)
            res['value']['trial_date_end'] = dEnd.strftime(OE_DFORMAT)

        return res

    def get_latest_initial_values(self, cr, uid, today_str=None, context=None):
        '''Return a record with an effective date before today_str but greater than all others'''

        init_obj = self.pool.get('hr.contract.init')
        if today_str == None:
            today_str = datetime.now().strftime(OE_DFORMAT)
        dToday = datetime.strptime(today_str, OE_DFORMAT).date()

        res = None
        ids = init_obj.search(
            cr, uid, [('date', '<=', today_str), ('state', '=', 'approve')],
            context=context)
        for init in init_obj.browse(cr, uid, ids, context=context):
            d = datetime.strptime(init.date, OE_DFORMAT).date()
            if d <= dToday:
                if res == None:
                    res = init
                elif d > datetime.strptime(res.date, OE_DFORMAT).date():
                    res = init

        return res
