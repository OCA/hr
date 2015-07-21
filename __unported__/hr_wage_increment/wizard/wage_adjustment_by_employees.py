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

from openerp.osv import fields, orm
from openerp.tools.translate import _


class hr_payslip_employees(orm.TransientModel):

    _name = 'wage.adjustment.employees'
    _description = 'Generate wage adjustments for selected employees'

    _columns = {
        'employee_ids': fields.many2many(
            'hr.employee',
            'hr_employee_wage_group_rel',
            'adjustment_id',
            'employee_id',
            'Employees',
        ),
    }

    def _calculate_adjustment(self, initial, adj_type, adj_amount):

        result = 0
        if adj_type == 'fixed':
            result = initial + adj_amount
        elif adj_type == 'percent':
            result = initial + (initial * adj_amount / 100)
        elif adj_type == 'final':
            result = adj_amount
        else:
            # manual
            result = initial

        return result

    def create_adjustments(self, cr, uid, ids, context=None):

        emp_pool = self.pool.get('hr.employee')
        adj_pool = self.pool.get('hr.contract.wage.increment')
        run_pool = self.pool.get('hr.contract.wage.increment.run')

        if context is None:
            context = {}

        data = self.read(cr, uid, ids, context=context)[0]
        if not data['employee_ids']:
            raise orm.except_orm(
                _("Warning !"),
                _("You must select at least one employee to generate wage "
                  "adjustments.")
            )

        run_id = context.get('active_id', False)
        if not run_id:
            raise orm.except_orm(_('Internal Error'), _(
                'Unable to determine wage adjustment run ID'))

        run_data = run_pool.read(
            cr, uid, run_id, ['effective_date', 'type', 'adjustment_amount'],
            context=context)

        for emp in emp_pool.browse(
                cr, uid, data['employee_ids'], context=context):

            # skip contracts that don't start before the effective date of the
            # adjustment
            if (run_data.get('effective_date') and
                    run_data['effective_date'] <=
                    emp.contract_id.date_start):
                continue

            res = {
                'effective_date': run_data.get('effective_date', False),
                'contract_id': emp.contract_id.id,
                'wage': self._calculate_adjustment(
                    emp.contract_id.wage, run_data['type'],
                    run_data['adjustment_amount']
                ),
                'run_id': run_id,
            }
            adj_pool.create(cr, uid, res, context=context)

        return {
            'type': 'ir.actions.act_window_close',
        }
