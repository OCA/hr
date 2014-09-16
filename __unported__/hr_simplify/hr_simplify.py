#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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

from osv import fields, osv
from tools.translate import _


class hr_employee(osv.osv):

    """Simplified Employee Record Interface."""

    _name = 'hr.employee'
    _inherit = 'hr.employee'

    def _get_latest_contract(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        obj_contract = self.pool.get('hr.contract')
        for emp in self.browse(cr, uid, ids, context=context):
            contract_ids = obj_contract.search(
                cr, uid, [('employee_id', '=', emp.id), ], order='date_start', context=context)
            if contract_ids:
                res[emp.id] = contract_ids[-1:][0]
            else:
                res[emp.id] = False
        return res

    def _get_id_from_contract(self, cr, uid, ids, context=None):

        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, ids, context=context):
            res.append(contract.employee_id.id)

        return res

    _columns = {
        'contract_id': fields.function(_get_latest_contract, string='Contract', type='many2one', relation="hr.contract",
                                       store={
                                           'hr.contract': (_get_id_from_contract, ['id', 'date_start'], 10)},
                                       help='Latest contract of the employee'),
        'job_id': fields.related('contract_id', 'job_id', type="many2one", obj="hr.job", string="Job",
                                 method=True, readonly=True, store={
                                     'hr.contract': (_get_id_from_contract, ['employee_id', 'job_id'], 10),
                                     'hr.employee': (lambda self, cr, uid, ids, context={}: ids, ['contract_id', 'active'], 10),
                                 }),
    }

    _sql_constraints = [
        ('unique_identification_id', 'unique(identification_id)',
         _('Official Identifications must be unique!')),
    ]

    def _default_country(self, cr, uid, context=None):

        cid = self.pool.get('res.country').search(
            cr, uid, [('code', '=', 'ET')], context=context)
        if cid:
            return cid[0]

    _defaults = {
        'country_id': _default_country,
    }

hr_employee()


class hr_contract(osv.osv):

    _inherit = 'hr.contract'

    _columns = {
        'employee_dept_id': fields.related('employee_id',
                                           'department_id',
                                           type='many2one',
                                           relation='hr.department',
                                           string="Default Dept Id"),
    }

    def _default_employee(self, cr, uid, context=None):

        if context != None:
            e_ids = context.get('search_default_employee_id', False)
            if e_ids:
                return e_ids[0]

    _defaults = {
        'employee_id': _default_employee,
    }

    def onchange_employee_id(self, cr, uid, ids, employee_id, context=None):

        dom = {
            'job_id': [],
        }
        val = {
            'employee_dept_id': [],
        }
        if employee_id:
            dept_id = self.pool.get('hr.employee').browse(cr, uid, employee_id,
                                                          context=context).department_id.id
            dom['job_id'] = [('department_id', '=', dept_id)]
            val['employee_dept_id'] = dept_id
        return {'value': val, 'domain': dom}


class hr_job(osv.osv):

    def _no_of_contracts(self, cr, uid, ids, name, args, context=None):
        res = {}
        for job in self.browse(cr, uid, ids, context=context):
            contract_ids = self.pool.get(
                'hr.contract').search(cr, uid, [('job_id', '=', job.id),
                                                ('state', '!=', 'done')],
                                      context=context)
            nb = len(contract_ids or [])
            res[job.id] = {
                'no_of_employee': nb,
                'expected_employees': nb + job.no_of_recruitment,
            }
        return res

    def _get_job_position(self, cr, uid, ids, context=None):
        res = []
        for contract in self.pool.get('hr.contract').browse(cr, uid, ids, context=context):
            if contract.job_id:
                res.append(contract.job_id.id)
        return res

    _name = 'hr.job'
    _inherit = 'hr.job'

    _columns = {
        'no_of_employee': fields.function(_no_of_contracts, string="Current Number of Employees",
                                          help='Number of employees currently occupying this job position.',
                                          store={
                                              'hr.contract': (_get_job_position, ['job_id'], 10),
                                          }, multi='no_of_employee'),
        'expected_employees': fields.function(_no_of_contracts, string='Total Forecasted Employees',
                                              help='Expected number of employees for this job position after new recruitment.',
                                              store={
                                                  'hr.job': (lambda self, cr, uid, ids, c=None: ids, ['no_of_recruitment'], 10),
                                                  'hr.contract': (_get_job_position, ['job_id'], 10),
                                              },
                                              multi='no_of_employee'),
    }
