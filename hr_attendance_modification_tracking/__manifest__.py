# Copyright 2019 Creu Blanca
# Copyright 2020 Landoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'HR Attendance Modification Tracking',
    'summary': """
        Attendance changes will now be registered in the chatter.""",
    'version': '12.0.1.1.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca, Landoo, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_attendance',
        'mail',
    ],
    'data': [
        'views/hr_attendance_view.xml',
    ],
    'installable': True,
}
