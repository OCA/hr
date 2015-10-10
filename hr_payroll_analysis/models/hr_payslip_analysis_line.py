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
from openerp import models, fields


class HrPayslipAnalysisLine(models.Model):
    _name = 'hr.payslip.analysis.line'

    payslip_id = fields.Many2one(
        'hr.payslip',
        'Payslip',
        required=True,
        ondelete="cascade",
    )
    payslip_line_id = fields.Many2one(
        'hr.payslip.line',
        'Payslip Line',
        required=True,
        ondelete="cascade"
    )
    salary_rule_id = fields.Many2one(
        'hr.salary.rule',
        'Salary Rule',
        required=True,
        index=True
    )
    company_id = fields.Many2one(
        'res.company',
        'Company',
        required=True,
        index=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        index=True
    )
    date = fields.Date(
        'Date',
        required=True
    )
    amount = fields.Float(
        'Amount',
        required=True,
    )
