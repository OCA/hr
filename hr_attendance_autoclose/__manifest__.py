# Copyright 2018 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'HR Attendance Auto Close',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Close stale Attendances',
    'website': 'https://github.com/OCA/hr',
    'author': 'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'depends': [
        'hr_attendance_reason',
    ],
    'data': [
        'data/hr_attendance_reason.xml',
        'data/hr_attendance.xml',
        'views/hr_attendance_view.xml',
        'views/res_company_view.xml',
    ],
}
