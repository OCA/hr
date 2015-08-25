{
    'name': 'Employee ID',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'Michael Telahun Makonnen, '
              'Salton Massally (iDT Labs), '
              'Odoo Community Association (OCA)',
    'website': 'http://miketelahun.wordpress.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'views/res_config_views.xml',
        'views/hr_employee_views.xml',
        'data/hr_employee_sequence.xml',
    ],
    'installable': False,
}
