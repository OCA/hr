# Copyright 2020 Supakorn Kimhajan (<supakorn.kim@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR employee working shift',
    'version': '12.0.1.0.0',
    'author': 'Supakorn Kimhajan <supakorn.kim@gmail.com>, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr/',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee_working_shift_view.xml',
    ],
    'installable': True,
}
