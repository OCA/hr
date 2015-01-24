# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 - 2015 Savoir-faire Linux. All Rights Reserved.
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

{
    'name': 'Employer Contribution',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Employer Contribution
=====================
Allows to create payroll structures that sum over the payslip lines of
every employee in a company.

This is required when a contribution of the employer must be
computated over the wage bill instead of every single payslip.

In your salary rules, you may access the contribution object with
"contribution.your_method_or_attribute"

You may sum over the payslips for the contribution's company with
"payslip.sum('Salary_rule_code', date_from, date_to)"

Salary rule variables can be used like in payslip with
"contribution.get_rule_variable(rule_id, contribution.date_from)"

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
        'hr_salary_rule_variable',
    ],
    'data': [
        'security/ir.model.access.csv',
        'workflow/hr_employer_contribution_workflow.xml',
        'view/hr_employer_contribution_view.xml',
        'view/hr_payslip_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
