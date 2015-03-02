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
    'name': 'Payroll Period',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Easy Payroll Management
=======================
This module implements a more formal payroll cycle.
This cycle is based on payroll period schedules configured by the user.
An end-of-pay-period wizard guides the HR officer or manager through
the payroll process. For each payroll period a specific set
of criteria have to be met in order to proceed to the next stage of the
process. For example:
    - Attendance records are complete
    """,
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_contract',
        'hr_contract_init',
        'hr_employee_state',
        'hr_payroll',
        'hr_payroll_register',
        'hr_payslip_amendment',
        'hr_public_holidays',
        'hr_schedule',
        'hr_security',
    ],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_payroll_period_data.xml',
        'data/mail_group_data.xml',
        'wizard/payroll_period_end_view.xml',
        'hr_payroll_period_view.xml',
        'hr_attendance_workflow.xml',
        'hr_payroll_period_workflow.xml',
        'hr_payroll_period_cron.xml',
    ],
    'test': [
    ],
    'installable': True,
}
