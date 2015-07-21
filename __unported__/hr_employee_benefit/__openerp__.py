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
    'name': 'Employee Benefit',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'description': """
Employee Benefit
================
This module implements employee benefits in order to produce payslips.

Employee benefits can be computed automatically at a specific point in a
payroll structure. They can also be computed using the button on the
payslip form, in the 'Employee Benefits' tab.

Also, they can be added manually on a payslip.

If a benefit has 2 different rates in the same payslip period,
the 2 rates will be weighted by the fraction of the payslip over which they
apply.
    """,
    'depends': [
        'hr_payroll',
        'hr_salary_rule_reference',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract.xml',
        'views/hr_employee_benefit_category.xml',
        'views/hr_employee_benefit_rate.xml',
        'views/hr_salary_rule.xml',
        'views/hr_payslip.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
