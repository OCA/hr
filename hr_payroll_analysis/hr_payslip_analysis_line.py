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


from openerp.osv import orm, fields


class hr_payslip_analysis_line(orm.Model):
    _name = 'hr.payslip.analysis.line'

    _columns = {
        'payslip_id': fields.many2one(
            'hr.payslip',
            'Payslip',
            required=True,
            ondelete="cascade",
        ),
        'payslip_line_id': fields.many2one(
            'hr.payslip.line',
            'Payslip Line',
            required=True,
            ondelete="cascade",
        ),
        'salary_rule_id': fields.many2one(
            'hr.salary.rule',
            'Salary Rule',
            required=True,
            select=True,
        ),
        'company_id': fields.many2one(
            'res.company',
            'Company',
            required=True,
            select=True,
        ),
        'employee_id': fields.many2one(
            'hr.employee',
            'Employee',
            required=True,
            select=True,
        ),
        'date': fields.date(
            'Date',
            required=True,
        ),
        'amount': fields.float(
            'Amount',
            required=True,
        ),
    }
