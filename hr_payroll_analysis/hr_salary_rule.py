# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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


class hr_salary_rule(orm.Model):
    _inherit = 'hr.salary.rule'

    _columns = {
        'include_in_payroll_analysis': fields.boolean(
            'Include in Payroll Analysis',
            help="If True, every payslip line related to this salary "
            "rule will appear in the payroll analysis report."
        ),
    }

    def write(self, cr, uid, ids, vals, context=None):
        res = super(hr_salary_rule, self).write(
            cr, uid, ids, vals, context=context)

        if 'include_in_payroll_analysis' in vals:
            self.refresh_analysis_lines(cr, uid, ids, context=context)

        return res

    def refresh_analysis_lines(self, cr, uid, ids, context=None):
        """This method is used to refresh the analysis lines
        when a salary rule's include_in_payroll_analysis field is changed
        """
        analysis_line_obj = self.pool['hr.payslip.analysis.line']
        payslip_line_obj = self.pool['hr.payslip.line']

        for rule in self.browse(cr, uid, ids, context=context):
            # Remove existing analysis lines
            line_ids = analysis_line_obj.search(
                cr, uid, [('salary_rule_id', '=', rule.id)],
                context=context)

            analysis_line_obj.unlink(cr, uid, line_ids, context=context)

            if rule.include_in_payroll_analysis:
                # Create analysis lines
                payslip_line_ids = payslip_line_obj.search(
                    cr, uid, [
                        ('salary_rule_id', '=', rule.id),
                        ('slip_id.state', 'not in', ['draft', 'cancel']),
                        ('total', '!=', 0),
                    ], context=context)

                for line in payslip_line_obj.browse(
                        cr, uid, payslip_line_ids, context=context):
                    payslip = line.slip_id
                    analysis_line_obj.create(
                        cr, uid, {
                            'company_id': payslip.company_id.id,
                            'employee_id': payslip.employee_id.id,
                            'salary_rule_id': line.salary_rule_id.id,
                            'payslip_line_id': line.id,
                            'payslip_id': payslip.id,
                            'date': payslip.date_from,
                            'amount': payslip.credit_note and -line.total or
                            line.total,
                        }, context=context)
