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


class hr_payslip(orm.Model):
    _inherit = 'hr.payslip'
    _columns = {
        'analysis_line_ids': fields.one2many(
            'hr.payslip.analysis.line',
            'payslip_id',
            'Analysis Lines',
        ),
    }

    def process_sheet(self, cr, uid, ids, context=None):
        """
        Create the analysis lines when the payslip is confirmed
        """
        super(hr_payslip, self).process_sheet(cr, uid, ids, context=context)

        self.remove_analysis_lines(cr, uid, ids, context=context)
        self.compute_analysis_lines(cr, uid, ids, context=context)

    def remove_analysis_lines(self, cr, uid, ids, context=None):
        """
        Make sure no analysis line has already been computed
        """
        for payslip in self.browse(cr, uid, ids, context=context):
            for line in payslip.analysis_line_ids:
                line.unlink()

    def compute_analysis_lines(self, cr, uid, ids, context=None):

        analysis_line_obj = self.pool['hr.payslip.analysis.line']

        for payslip in self.browse(cr, uid, ids, context=context):

            required_lines = [
                line for line in payslip.details_by_salary_rule_category
                if line.salary_rule_id.include_in_payroll_analysis
                and line.total
            ]

            is_refund = payslip.credit_note

            for line in required_lines:
                analysis_line_obj.create(
                    cr, uid, {
                        'company_id': payslip.company_id.id,
                        'employee_id': payslip.employee_id.id,
                        'salary_rule_id': line.salary_rule_id.id,
                        'payslip_line_id': line.id,
                        'payslip_id': payslip.id,
                        'date': payslip.date_from,
                        'amount': is_refund and -line.total or line.total,
                    }, context=context)

    def cancel_sheet(self, cr, uid, ids, context=None):
        """
        Make sure no analytic lines exist when a payslip is cancelled
        """
        self.remove_analysis_lines(cr, uid, ids, context=context)
        super(hr_payslip, self).cancel_sheet(cr, uid, ids, context=context)
