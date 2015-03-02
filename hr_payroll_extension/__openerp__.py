# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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
#

{
    'name': 'Payroll Extension',
    'category': 'Human Resources',
    'author': "Michael Telahun Makonnen,Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'version': '1.0',
    'description': """
Extended set of Payroll Rules and Structures
============================================

    - Detailed calculation of worked hours, leaves, overtime, etc
    - Overtime
    - Paid and Unpaid Leaves
    - Federal Income Tax Withholding rules
    - Provident/Pension Fund contributions
    - Various Earnings and Deductions
    - Payroll Report
    """,
    'depends': [
        'hr_attendance',
        'hr_payroll',
        'hr_payroll_period',
        'hr_policy_absence',
        'hr_policy_ot',
        'hr_policy_presence',
        'hr_public_holidays',
        'hr_schedule',
    ],
    'data': [
        'data/hr_payroll_extension_data.xml',
        'data/hr.salary.rule.csv',
        'hr_payroll_view.xml',
    ],
    'test': [
    ],
    'installable': True,
}
