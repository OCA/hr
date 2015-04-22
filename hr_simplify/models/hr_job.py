# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
##############################################################################

from openerp import models, fields, api


class hr_job(models.Model):

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
        for contract in self.pool.get('hr.contract').browse(
            cr, uid, ids, context=context
        ):
            if contract.job_id:
                res.append(contract.job_id.id)
        return res

    _name = 'hr.job'
    _inherit = 'hr.job'

    _columns = {
        'no_of_employee': fields.function(
            _no_of_contracts,
            string="Current Number of Employees",
            help='Number of employees currently occupying this job position.',
            store={
                'hr.contract': (_get_job_position, ['job_id'], 10),
            },
            multi='no_of_employee',
        ),
        'expected_employees': fields.function(
            _no_of_contracts,
            string='Total Forecasted Employees',
            help='Expected number of employees for this job position after new'
                 ' recruitment.',
            store={
                'hr.job': (
                    lambda self, cr, uid, ids, c=None: ids,
                    ['no_of_recruitment'], 10),
                'hr.contract': (_get_job_position, ['job_id'], 10),
            },
            multi='no_of_employee',
        ),
    }
