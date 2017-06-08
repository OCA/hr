# -*- coding: utf-8 -*-
# © 2016 Ergobit Consulting (https://www.ergobit.org)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'HR Payroll Total YTD',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'author': "Ergobit Consulting, Odoo Community Association (OCA)",
    'website': 'https://ergobit.org',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'report/report_payslip.xml',
        'views/hr_payslip.xml',
    ],
    'installable': True,
}
