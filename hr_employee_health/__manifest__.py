# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Employee Health',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Allows storing information about employee\'s health',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/data_health_condition_type.xml',
        'data/data_health_condition_severity.xml',
        'data/data_blood_type.xml',
        'views/hr_employee.xml',
        'views/hr_employee_health_condition.xml',
    ],
}
