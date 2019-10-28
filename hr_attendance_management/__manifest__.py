# -*- coding: utf-8 -*-
##############################################################################
#
#       ______ Releasing children from poverty      _
#      / ____/___  ____ ___  ____  ____ ___________(_)___  ____
#     / /   / __ \/ __ `__ \/ __ \/ __ `/ ___/ ___/ / __ \/ __ \
#    / /___/ /_/ / / / / / / /_/ / /_/ (__  |__  ) / /_/ / / / /
#    \____/\____/_/ /_/ /_/ .___/\__,_/____/____/_/\____/_/ /_/
#                        /_/
#                            in Jesus' name
#
#    Copyright (C) 2018 Compassion CH (http://www.compassion.ch)
#    @author: Stephane Eicher <seicher@compassion.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'HR (Extra) Hours Management',
    'summary': 'Compute extra hours based on attendances',
    'category': 'Human Resources',
    'author': "Compassion Switzerland, "
              "Odoo Community Association (OCA)",
    'depends': [
        'hr_attendance',
        'hr_public_holidays',
        'hr_contract'
    ],
    'version': '10.0.3.1.0',
    'auto_install': False,
    'website': 'https://www.compassion.ch',
    'license': 'AGPL-3',
    'images': [],
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_create_period_wizard_view.xml',
        'views/hr_attendance_calendar_view.xml',
        'views/hr_attendance_day_view.xml',
        'views/hr_attendance_settings.xml',
        'views/hr_attendance_view.xml',
        'views/hr_employee.xml',
        'views/hr_holidays_status_views.xml',
        'views/hr_holidays_views.xml',
        'views/attendance.xml',
        'views/hr_attendance_break.xml',
        'views/hr_attendance_location.xml',
        'views/hr_employee_periods.xml',
        'data/attendance_computation_cron.xml',
        'data/annual_balance_cron.xml',
        'data/hr_attendance_settings.xml',
        'views/extra_hours_evolution_graph.xml',
        'views/hr_change_day_wizard_view.xml',
        'views/hr_change_day_requests.xml'
    ],
    'demo': [
        'demo/hr_config.xml',
        'demo/resource_calendar.xml',
        'demo/hr_attendance_day.xml',
        'demo/hr_contract.xml',
    ],
    'installable': True,
    'qweb': [
        "static/src/xml/attendance.xml",
    ],
}
