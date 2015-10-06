# -*- coding:utf-8 -*-
from openerp import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    analysis_line_ids = fields.One2many('hr.payslip.analysis.line', 
                                        'payslip_id', 'Analysis Lines')

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
        for payslip in self:
            for line in payslip.analysis_line_ids:
                line.unlink()
    
    @api.multi
    def compute_analysis_lines(self):

        analysis_line_obj = self.env['hr.payslip.analysis.line']

        for payslip in self:

            required_lines = [
                line for line in payslip.details_by_salary_rule_category
                if line.salary_rule_id.include_in_payroll_analysis and
                line.total
            ]

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
