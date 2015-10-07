# -*- coding:utf-8 -*-

{
    'name': 'Payroll Contribution Register Report',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': "Print Contribution register from payroll run",
    'author': "Salton Massally <smassally@idtlabs.sl>, "
               "Odoo Community Association (OCA)",
    'website': 'http://idtlabs.sl',
    'license': 'AGPL-3',
    'depends': ['hr_payroll'],
    'data': [
        'wizard/print_contribution_register_view.xml',
        'contrib_register_report.xml'
    ],
    'installable': True,
}
