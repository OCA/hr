# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Employee own info',
    'summary': 'Employee can see own information',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/hr/',
    'category': 'Human Resources',
    'version': '11.0.1.0.0',
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_employee.xml',
    ],
    'installable': True,
}
