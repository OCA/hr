# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Attendance Modification Tracking',
    'summary': """
        Attendance changes will now be registered in the chatter.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_attendance',
        'mail',
    ],
    'data': [
        'views/hr_attendance_view.xml',
    ],
}
