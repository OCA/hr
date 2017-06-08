# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    analysis_line_ids = fields.One2many(
        'hr.payslip.analysis.line',
        'payslip_id',
        'Analysis Lines'
    )

    @api.multi
    def process_sheet(self):
        """
        Create the analysis lines when the payslip is confirmed
        """
        super(HrPayslip, self).process_sheet()
        self.remove_analysis_lines()
        self.compute_analysis_lines()

    @api.multi
    def remove_analysis_lines(self):
        """
        Make sure no analysis line has already been computed
        """
        self.mapped('analysis_line_ids').unlink()

    @api.multi
    def compute_analysis_lines(self):

        analysis_line_obj = self.env['hr.payslip.analysis.line']

        for payslip in self:
            required_lines = payslip.details_by_salary_rule_category.filtered(
                lambda line: line.salary_rule_id.include_in_payroll_analysis
                and line.total)

            is_refund = payslip.credit_note

            for line in required_lines:
                analysis_line_obj.create(
                    {
                        'company_id': payslip.company_id.id,
                        'employee_id': payslip.employee_id.id,
                        'salary_rule_id': line.salary_rule_id.id,
                        'payslip_line_id': line.id,
                        'payslip_id': payslip.id,
                        'date': payslip.date_from,
                        'amount': is_refund and -line.total or line.total,
                    })

    @api.multi
    def cancel_sheet(self):
        """
        Make sure no analytic lines exist when a payslip is cancelled
        """
        self.remove_analysis_lines()
        super(HrPayslip, self).cancel_sheet()
