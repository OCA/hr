#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
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
#

{
    'name': 'Employee Shift Scheduling',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Employee Shift Scheduling
=========================

Easily create, manage, and track employee schedules.
    """,
    'author': 'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_attendance',
        'hr_contract',
        'hr_contract_init',
        'hr_employee_state',
        'hr_holidays',
        'hr_security',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/hr_schedule_data.xml',
        'hr_schedule_view.xml',
        'wizard/validate_schedule_view.xml',
        'wizard/compute_alerts_view.xml',
        'wizard/generate_schedules_view.xml',
        'wizard/restday_view.xml',
        'hr_schedule_data.xml',
        'hr_schedule_workflow.xml',
        'hr_schedule_cron.xml',
        'alert_rule_data.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
