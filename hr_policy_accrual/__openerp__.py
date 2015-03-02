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
    'name': 'Time Accrual Policy',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Define Time Accrual Policies
============================
Define properties of a leave accrual policy. The accrued time is calculated
based on the length of service of the employee. An additional premium may be
added on the base rate based on additional months of service.
This policy is ideal for annual leave accruals. If the type of accrual is
'Standard' time is accrued and withdrawn manually. However, if the type is
'Calendar' the time is accrued (and recorded) at a fixed frequency.
    """,
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_accrual',
        'hr_contract_state',
        'hr_employee_seniority',
        'hr_policy_group',
    ],
    'data': [
        'security/ir.model.access.csv',
        'hr_policy_accrual_cron.xml',
        'hr_policy_accrual_view.xml',
    ],
    'test': [
    ],
    'installable': True,
}
