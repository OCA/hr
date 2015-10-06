# -*- coding:utf-8 -*-
import pytz
from datetime import datetime, date

from openerp import models, fields, api, _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


def get_current_year(context):
    if not context:
        context = {}
    tz = context.get('tz', False)
    tz = tz and pytz.timezone(tz) or pytz.utc
    return datetime.now(tz).year


class PayrollAnalysis(models.TransientModel):
    """
    Wizard to generate payroll analysis report
    """
    _name = 'hr.payroll.analysis'
    _description = 'Payroll Analysis Wizard'

    type = fields.Selection(
        [
            ('employee', 'By Employee'),
            ('salary_rule', 'By Salary Rule'),
            ('company', 'By Company'),
        ], required=True,  string="Analysis Type", default='salary_rule')
    period = fields.Selection(
        [
            ('current_year', 'Current Year'),
            ('previous_year', 'Previous Year'),
            ('every_year', 'Every Year'),
        ], string='Analysis Period', default='current_year')
    start_date = fields.Datetime('Start Date',
        default=lambda self: (
            date(get_current_year(self.env.context), 1, 1).strftime(
                DEFAULT_SERVER_DATE_FORMAT)))
    end_date = fields.Datetime('End Date',
        default=lambda self: (
            date(get_current_year(self.env.context), 12, 31).strftime(
                DEFAULT_SERVER_DATE_FORMAT)))
    company_ids = fields.Many2many('res.company',
        'payroll_analysis_company_rel', 'payroll_analysis_id',
        'company_id', 'Companies',)
    employee_ids = fields.Many2many('hr.employee',
        'payroll_analysis_employee_rel', 'payroll_analysis_id',
        'employee_id', 'Employees',)
    salary_rule_ids = fields.Many2many('hr.salary.rule',
        'payroll_analysis_salary_rule_rel', 'payroll_analysis_id',
        'salary_rule_id','Salary Rules',)

    @api.onchange('period')
    @api.one
    def onchange_period(self):
        if self.period:
            if self.period == 'every_year':
                self.start_date = False
                self.end_date = False
    
            year = get_current_year(self.env.context)
    
            if self.period == 'previous_year':
                year -= 1
    
            start_date = date(year, 1, 1).strftime(DEFAULT_SERVER_DATE_FORMAT)
            end_date = date(year, 12, 31).strftime(DEFAULT_SERVER_DATE_FORMAT)
    
            self.start_date = start_date
            self.end_date = end_date
    
    @api.multi
    def payroll_analysis_open_window(self):
        """
        This method returns an action that displays profitability lines
        requested in the wizard
        """
        self.ensure_one()
        wizard = self[0]

        domain_filters = []

        if wizard.salary_rule_ids:
            domain_filters.append(('salary_rule_id', 'in', [
                rule.id for rule in wizard.salary_rule_ids]))

        if wizard.employee_ids and wizard.type == 'employee':
            domain_filters.append(('employee_id', 'in', [
                employee.id for employee in wizard.employee_ids]))

        if wizard.company_ids and wizard.type == 'company':
            domain_filters.append(('company_id', 'in', [
                company.id for company in wizard.company_ids]))

        if wizard.end_date:
            domain_filters.append(('date', '<=', wizard.end_date))

        if wizard.start_date:
            domain_filters.append(('date', '>=', wizard.start_date))

        analysis_lines = self.env['hr.payslip.analysis.line'].search(
                                                            domain_filters)
        analysis_line_ids = analysis_lines.mapped('id')

        view_ref = \
            self.env.ref('hr_payroll_analysis.view_payslip_analysis_line_tree')

        view_context = {}

        if wizard.type == 'company':
            view_context = {
                'search_default_group_company_id': 1,
                'search_default_group_salary_rule_id': 1,
            }
        elif wizard.type == 'employee':
            view_context = {
                'search_default_group_employee_id': 1,
                'search_default_group_salary_rule_id': 1,
            }
        elif wizard.type == 'salary_rule':
            view_context = {
                'search_default_group_salary_rule_id': 1,
            }

        view_id = view_ref and view_ref.id or False

        return {
            'type': 'ir.actions.act_window',
            'name': _('Payroll Analysis'),
            'res_model': 'hr.payslip.analysis.line',
            'view_type': 'list',
            'view_mode': 'list',
            'view_id': view_id,
            'domain': [('id', 'in', analysis_line_ids)],
            'context': view_context,
        }
