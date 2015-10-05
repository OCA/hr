# -*- coding:utf-8 -*-

{
    'name': 'Employee Service Length',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': "Calculates the length of an employee's time in a company",
    'author': "Salton Massally <smassally@idtlabs.sl>, "
               "Odoo Community Association (OCA)",
    'website': 'http://idtlabs.sl',
    'license': 'AGPL-3',
    'depends': ['hr_contract_usability'],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'views/hr_employee.xml',
    ],
    'installable': True,
}
