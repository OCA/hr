# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
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

from openerp.osv import orm, fields
from openerp.tools.translate import _


class hr_payslip_employees(orm.TransientModel):
    """
    Add the possibility to import worked days from timesheet
    """
    _inherit = 'hr.payslip.employees'
    _columns = {
        'employee_ids': fields.many2many(
            'hr.employee',
            'hr_employee_group_rel',
            'payslip_id',
            'employee_id',
            'Employees'
        ),
        'import_from_timesheet': fields.boolean(
            'Import Worked Days From Timesheet',
        ),
    }

    def compute_sheet(self, cr, uid, ids, context=None):
        """
        If import_from_timesheet boolean is True,
        import worked days before computing each payslip,
        othewise, only compute the payslips.
        """
        payslip_employees = self.browse(cr, uid, ids, context=context)[0]

        if not payslip_employees.import_from_timesheet:
            return super(hr_payslip_employees, self).compute_sheet(
                cr, uid, ids, context=context)

        employee_pool = self.pool['hr.employee']
        slip_pool = self.pool['hr.payslip']
        payslip_run = self.pool['hr.payslip.run'].browse(
            cr, uid, context['active_id'], context=context)

        if not payslip_employees.employee_ids:
            raise orm.except_orm(
                _("Warning!"),
                _("You must select employee(s) to generate payslip(s).")
            )

        employee_ids = [e.id for e in payslip_employees.employee_ids]
        employees = employee_pool.browse(
            cr, uid, employee_ids, context=context)
        slip_ids = []

        from_date = payslip_run.date_start
        to_date = payslip_run.date_end
        credit_note = payslip_run.credit_note

        # Make sure that every employee selected completed has at least one
        # approved timesheet for the run period
        # Otherwise, an exception will be raised to alert the user.
        for employee in employees:
            slip_pool.get_timesheets_from_employee(
                cr, uid,
                employee.id,
                from_date, to_date,
                context=context
            )

        for employee in employees:
            slip_data = slip_pool.onchange_employee_id(
                cr, uid, [],
                from_date, to_date, employee.id,
                contract_id=False, context=context
            )

            res = {
                'employee_id': employee.id,
                'name': slip_data['value'].get('name', False),
                'struct_id': slip_data['value'].get('struct_id', False),
                'contract_id': slip_data['value'].get('contract_id', False),
                'payslip_run_id': context.get('active_id', False),
                'input_line_ids': [
                    (0, 0, x) for x
                    in slip_data['value'].get('input_line_ids', False)
                ],
                'worked_days_line_ids': [
                    (0, 0, x) for x
                    in slip_data['value'].get('worked_days_line_ids', False)
                ],
                'date_from': from_date,
                'date_to': to_date,
                'credit_note': credit_note,
            }

            slip_ids.append(slip_pool.create(cr, uid, res, context=context))

        # Import worked days from timesheet
        slip_pool.import_worked_days(cr, uid, slip_ids, context=context)

        slip_pool.compute_sheet(cr, uid, slip_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}
