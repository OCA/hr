# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'HR Attendance Split',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Split attendance entries into two if they cross midnight',
    'website': 'https://github.com/OCA/hr',
    'author': 'Odoo S.A.,'
              'Odoo Community Association (OCA)',
    'license': 'LGPL-3',
    'installable': True,
    'depends': [
        'hr_attendance',
    ],
    'data': [
        'views/hr_attendance_view.xml',
        'views/res_config_settings_views.xml',
    ],
    'development_status': 'alpha',
}
