# -*- coding:utf-8 -*-
from openerp import models, fields, api


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    include_in_payroll_analysis = fields.Boolean(
        'Include in Payroll Analysis',
        help="If True, every payslip line related to this salary "
        "rule will appear in the payroll analysis report."
    )

    @api.multi
    def write(self, vals):
        res = super(HrSalaryRule, self).write(vals)
        if 'include_in_payroll_analysis' in vals:
            self.refresh_analysis_lines()
        return res

    @api.multi
    def refresh_analysis_lines(self):
        """This method is used to refresh the analysis lines
        when a salary rule's include_in_payroll_analysis field is changed
        """
        analysis_line_obj = self.env['hr.payslip.analysis.line']
        payslip_line_obj = self.env['hr.payslip.line']

        for rule in self:
            # Remove existing analysis lines
            lines = analysis_line_obj.search(
                                    [('salary_rule_id', '=', rule.id)])
            lines.unlink()

            if rule.include_in_payroll_analysis:
                # Create analysis lines
                payslip_lines = payslip_line_obj.search(
                    [
                        ('salary_rule_id', '=', rule.id),
                        ('slip_id.state', 'not in', ['draft', 'cancel']),
                        ('total', '!=', 0),
                    ])

                for line in payslip_lines:
                    payslip = line.slip_id
                    analysis_line_obj.create(
                        {
                            'company_id': payslip.company_id.id,
                            'employee_id': payslip.employee_id.id,
                            'salary_rule_id': line.salary_rule_id.id,
                            'payslip_line_id': line.id,
                            'payslip_id': payslip.id,
                            'date': payslip.date_from,
                            'amount': payslip.credit_note and -line.total or
                            line.total,
                        })
