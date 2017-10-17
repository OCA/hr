# -*- coding: utf-8 -*-
# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Employee Passport',
    'summary': """
        Allow to store employee's passports""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr',
    ],
    'data': [
        'security/hr_employee_passport_acl.xml',
        'security/hr_employee_passport_rule.xml',
        'views/hr_employee.xml',
        'views/hr_employee_passport.xml',
    ],
}
