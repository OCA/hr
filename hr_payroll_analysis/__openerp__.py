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

{
    'name': 'Payroll Analysis',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Payroll Analysis
================
This module adds a report over amounts of payslips line related to a
a salary rule. It allows to group amounts by date, companies, salary rules
and employees.

This module replaces the use of contribution registers already implemented
in Odoo, which is meant to generate pdf reports. The purpose of this module
is to create dynamic reports.

To include salary rules in the report, in the salary rule form view,
check the field "Include in Payroll Analysis".

To view the report go to Reporting -> Human Ressources -> Payroll Analysis,
then fill the wizard.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'wizard/payroll_analysis_view.xml',
        'hr_salary_rule_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
