# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Calendar Rest Time',
    'summary': """
        Adds rest time to the calendar attendance records.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr',
        'resource_hook',
    ],
    'data': [
        'views/resource_calendar_attendance.xml',
    ],
}
