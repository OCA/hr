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

from openerp.osv import orm


class hr_payslip(orm.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self, cr, uid, ids, context=None):
        super(hr_payslip, self).compute_sheet(
            cr, uid, ids, context=context
        )
        self.compute_lines_ytd(cr, uid, ids, context=context)

    def compute_lines_ytd(self, cr, uid, ids, context=None):
        for payslip in self.browse(cr, uid, ids, context=context):
            # Create a dict of the required lines that will be used
            # to sum amounts over the payslips
            line_dict = {
                line.salary_rule_id.code: 0 for line in payslip.line_ids}

            # Get the payslips of the employee for the current year
            date_from = payslip.date_from[0:4] + "-01-01"

            employee_payslip_ids = self.search(
                cr, uid, [
                    ('employee_id', '=', payslip.employee_id.id),
                    ('date_from', '>=', date_from),
                    ('date_to', '<=', payslip.date_to),
                    ('state', '=', 'done'),
                ], context=context)

            employee_payslips = self.browse(
                cr, uid, employee_payslip_ids, context=context)

            # Iterate one time over each line of each payslip of the
            # employee since the beginning of the year and sum required
            # lines
            for emp_payslip in employee_payslips:
                is_refund = emp_payslip.credit_note and -1 or 1

                for line in emp_payslip.line_ids:
                    if line.salary_rule_id.code in line_dict:
                        line_dict[line.salary_rule_id.code] += \
                            line.total * is_refund

            # For each line in the payslip, write the related total ytd
            for line in payslip.line_ids:
                amount = line_dict[line.salary_rule_id.code] + line.total
                self.pool['hr.payslip.line'].write(
                    cr, uid, [line.id], {'total_ytd': amount}, context=context)
