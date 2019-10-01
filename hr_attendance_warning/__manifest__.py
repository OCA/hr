# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Attendance Warning',
    'summary': """
        This module allows you to get warnings when there are
        inconsistencies between the theoric check in time of an employee
        and what has happened.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr/',
    'depends': [
        'hr_holidays_public',
        'hr_attendance',
        'resource',
        'mail'
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'data/ir_config_parameter_data.xml',
        'data/check_issues_cron.xml',
        'security/hr_warnings_security.xml',
        'security/ir.model.access.csv',
        'views/assets_backend.xml',
        'views/hr_attendance_warning.xml',
        'views/resource_calendar_attendance.xml',
        'wizards/hr_attendance_warning_solve.xml',
    ],
    'qweb': [
        'static/src/xml/systray.xml',
    ],
}
