# -*- coding: utf-8 -*-
# © 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.

{
    'name': 'Employee Transfer',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'summary': "Transfer Employees between Jobs and Departments",
    'author': 'Michael Telahun Makonnen, '
              'Odoo Community Association (OCA)',
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_transfer_cron.xml',
        'data/hr_transfer_data.xml',
        'views/hr_transfer_view.xml',
        'data/hr_transfer_workflow.xml',
    ],

    'installable': True,
}
