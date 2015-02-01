# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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


class hr_payslip(orm.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _columns = {
        'leave_accrual_line_ids': fields.one2many(
            'hr.leave.accrual.line',
            'payslip_id',
            'Leave Accrual Lines',
        ),
    }

    def compute_sheet(self, cr, uid, ids, context=None):
        super(hr_payslip, self).compute_sheet(
            cr, uid, ids, context=context
        )
        self.compute_leave_accrual_lines(cr, uid, ids, context=context)

    def compute_leave_accrual_lines(self, cr, uid, ids, context=None):
        """
        Update an employee's leave accruals with the amounts computed in the
        payslip.
        """
        for payslip in self.browse(cr, uid, ids, context=context):
            # Get the required leave accruals
            salary_rule_ids = [
                line.salary_rule_id.id for line
                in payslip.details_by_salary_rule_category]

            line_obj = self.pool['hr.holidays.status.accrual.line']

            leave_accrual_line_ids = line_obj.search(
                cr, uid, [('salary_rule_id', 'in', salary_rule_ids)],
                context=context)

            leave_accrual_lines = line_obj.browse(
                cr, uid, leave_accrual_line_ids, context=context)

            leave_types_required = {
                line.leave_type_id for line in leave_accrual_lines}

            # Check if employee has every required leave accruals
            # If it does not exist, create it
            accrual_obj = self.pool['hr.leave.accrual']
            for leave_type in leave_types_required:
                if not accrual_obj.search(cr, uid, [
                    ('employee_id', '=', payslip.employee_id.id),
                    ('leave_type_id', '=', leave_type.id),
                ], context=context):
                    accrual_obj.create(cr, uid, {
                        'employee_id': payslip.employee_id.id,
                        'leave_type_id': leave_type.id,
                    }, context=context)

            # Get the set of codes needed from the the register templates
            accruals = payslip.employee_id.leave_accrual_ids

            # Retreive all lines from the leave types
            # This allows to know witch payslip lines are used to update the
            # leave accrual.
            required_rules = [
                line.salary_rule_id.id for line in leave_accrual_lines]

            # Create a dict to access the required payslip lines by rule id.
            # This is a matter of performance because we iterate
            # only one time over each payslip line
            payslip_line_dict = {
                line.salary_rule_id.id: line
                for line in payslip.details_by_salary_rule_category
                if line.salary_rule_id.id in required_rules
            }

            # Create a list of new register line records
            accrual_lines = []
            for accrual in accruals:
                # For each line in the accrual's leave_type,
                # Add a line in the accrual related to a payslip line.
                for line in accrual.leave_type_id.accrual_line_ids:
                    salary_rule_id = line.salary_rule_id.id

                    if(
                        # Check if the rule is in the payslip
                        salary_rule_id in payslip_line_dict
                    ):
                        # Get the payslip line related to the template line
                        payslip_line = payslip_line_dict[salary_rule_id]

                        amount = line.substract and payslip_line.amount * -1 \
                            or payslip_line.amount

                        if payslip_line.amount != 0:
                            accrual_lines.append((0, 0, {
                                'source': 'payslip',
                                'payslip_id': payslip.id,
                                'payslip_line_id': payslip_line.id,
                                'amount': amount,
                                'accrual_id': accrual.id,
                                'is_refund': payslip.credit_note,
                                'amount_type': line.amount_type,
                            }))

            # Write the resulting records
            self.write(
                cr, uid,
                [payslip.id],
                {'leave_accrual_line_ids': accrual_lines},
                context=context
            )
