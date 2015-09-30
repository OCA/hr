{
    'name': 'Pay Slip Amendment',
    'version': '1.0',
    'category': 'Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>, "
              "Salton Massally<smassally@idtlabs.sl>, "
              "Odoo Community Association (OCA)",
    'summary': "Add Amendments to Current and Future Pay Slips",
    'website': 'http://miketelahun.wordpress.com',
    'license': 'AGPL-3',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'views/hr_payslip_amendment_view.xml',
        'views/hr_payslip_amendment_workflow.xml',
    ],
    'installable': True,
}
