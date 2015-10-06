# -*- coding:utf-8 -*-
from openerp import models, fields, api


class HrPayslipAnalysisLine(models.Model):
    _name = 'hr.payslip.analysis.line'

    payslip_id = fields.Many2one('hr.payslip', 'Payslip', required=True,
                                 ondelete="cascade",)
    payslip_line_id = fields.Many2one('hr.payslip.line', 'Payslip Line',
                                      required=True, ondelete="cascade")
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Salary Rule', 
                                     required=True, index=True)
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 index=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,
                                  index=True)
    date = fields.Date('Date', required=True)
    amount= fields.Float('Amount', required=True,)
