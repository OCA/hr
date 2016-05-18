# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Commisions - Payroll',
    'summary': 'Payroll Commisions',
    'category': 'Human Resources',
    'author': "Open-Net Sàrl,Odoo Community Association (OCA)",
    'depends': [
        'hr_payroll',
        'account'
    ],
    'version': '9.0.1.0.0',
    'auto_install': False,
    'website': 'http://open-net.ch',
    'license': 'AGPL-3',
    'images': [],
    'data': [
        'views/hr_contract_view.xml',
        'views/hr_payroll_view.xml',
        'data/hr.salary.rule.xml',
    ],
    'installable': True
}
