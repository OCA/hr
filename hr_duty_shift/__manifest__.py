# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Duty Shift',
    'summary': """
        Define duty shifts on employees""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_holidays_public',
        'hr_attendance',
    ],
    'data': [
        'report/duty_shift_report.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/hr_duty_shift.xml',
        'views/hr_employee.xml',
        'wizards/wizard_duty_shift_report.xml',
    ],
}
