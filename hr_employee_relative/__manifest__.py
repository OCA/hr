# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Employee Relatives',
    'version': '12.0.1.1.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Allows storing information about employee\'s family',
    'depends': [
        'hr',
    ],
    'external_dependencies': {
        'python': [
            'dateutil',
        ],
    },
    'data': [
        'data/data_relative_relation.xml',
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_employee_relative.xml',
    ],
}
