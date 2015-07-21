# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
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

import pytz
from openerp.osv import orm, fields
from datetime import datetime, date
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _


def get_current_year(context):
    if not context:
        context = {}
    tz = context.get('tz', False)
    tz = tz and pytz.timezone(tz) or pytz.utc
    return datetime.now(tz).year


class payroll_analysis(orm.TransientModel):
    """
    Wizard to generate payroll analysis report
    """
    _name = 'hr.payroll.analysis'
    _description = 'Payroll Analysis Wizard'

    _columns = {
        'type': fields.selection(
            [
                ('employee', 'By Employee'),
                ('salary_rule', 'By Salary Rule'),
                ('company', 'By Company'),
            ],
            type="char",
            required=True,
            string="Analysis Type",
        ),
        'period': fields.selection(
            [
                ('current_year', 'Current Year'),
                ('previous_year', 'Previous Year'),
                ('every_year', 'Every Year'),
            ],
            string='Analysis Period',
            type='string',
        ),
        'start_date': fields.datetime('Start Date'),
        'end_date': fields.datetime('End Date'),
        'company_ids': fields.many2many(
            'res.company',
            'payroll_analysis_company_rel',
            'payroll_analysis_id',
            'company_id',
            'Companies',
        ),
        'employee_ids': fields.many2many(
            'hr.employee',
            'payroll_analysis_employee_rel',
            'payroll_analysis_id',
            'employee_id',
            'Employees',
        ),
        'salary_rule_ids': fields.many2many(
            'hr.salary.rule',
            'payroll_analysis_salary_rule_rel',
            'payroll_analysis_id',
            'salary_rule_id',
            'Salary Rules',
        ),
    }

    _defaults = {
        'start_date': lambda self, cr, uid, context: (
            date(get_current_year(context), 1, 1).strftime(
                DEFAULT_SERVER_DATE_FORMAT)),
        'end_date': lambda self, cr, uid, context: (
            date(get_current_year(context), 12, 31).strftime(
                DEFAULT_SERVER_DATE_FORMAT)),
        'period': 'current_year',
        'type': 'salary_rule',
    }

    def onchange_period(self, cr, uid, ids, period, context=None):
        if not period:
            return {}

        if period == 'every_year':
            return {'value': {
                'start_date': False,
                'end_date': False,
            }}

        year = get_current_year(context)

        if period == 'previous_year':
            year -= 1

        start_date = date(year, 1, 1).strftime(DEFAULT_SERVER_DATE_FORMAT)
        end_date = date(year, 12, 31).strftime(DEFAULT_SERVER_DATE_FORMAT)

        return {'value': {
            'start_date': start_date,
            'end_date': end_date,
        }}

    def payroll_analysis_open_window(self, cr, uid, ids, context=None):
        """
        This method returns an action that displays profitability lines
        requested in the wizard
        """
        if context is None:
            context = {}

        wizard = self.browse(cr, uid, ids, context=context)[0]

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

        analysis_line_ids = self.pool['hr.payslip.analysis.line'].search(
            cr, uid, domain_filters, context=context)

        view_ref = self.pool['ir.model.data'].get_object_reference(
            cr, uid, 'hr_payroll_analysis',
            'view_payslip_analysis_line_tree')

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

        view_id = view_ref and view_ref[1] or False

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
