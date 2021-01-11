# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Payment Difference on HR expenses',
    'version': '12.0.1.1.0',
    'category': 'Human Resources',
    'author': 'Ecosoft, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'wizards/hr_expense_sheet_register_payment.xml',
    ],
    'installable': True,
}
