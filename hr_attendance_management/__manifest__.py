# -*- coding: utf-8 -*-
# Copyright 2018 Stéphane Eicher <seicher@compassion.ch>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR (Extra) Hours Management',
    'summary': 'Compute and manage extra hours based on attendances',
    'category': 'Human Resources',
    'author': "Compassion Switzerland, "
              "Odoo Community Association (OCA)",
    'depends': [
        'hr_attendance',
        'hr_public_holidays',
        'hr_contract'
    ],
    'version': '10.0.1.1.0',
    'auto_install': False,
    'website': 'https://github.com/OCA/hr',
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/hr_attendance_calendar_view.xml',
        'views/hr_attendance_day_view.xml',
        'views/hr_attendance_settings.xml',
        'views/hr_attendance_view.xml',
        'views/hr_employee.xml',
        'views/hr_holidays_status_views.xml',
        'views/attendance.xml',
        'views/hr_attendance_break.xml',
        'data/attendance_computation_cron.xml',
        'data/annual_balance_cron.xml',
        'views/extra_hours_evolution_graph.xml',
        'views/hr_change_day_wizard_view.xml',
        'views/hr_change_day_requests.xml'
    ],
    'demo': [
        'demo/hr_config.xml',
        'demo/resource_calendar.xml',
    ],
    'installable': True,
    'qweb': [
        "static/src/xml/attendance.xml",
    ],
}
