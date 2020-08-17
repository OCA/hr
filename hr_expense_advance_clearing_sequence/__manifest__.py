# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    'name': 'HR Expense Advance Clearing Sequence',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'author': 'Ecosoft, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_expense_sequence',
        'hr_expense_advance_clearing',
    ],
    'data': [
        'data/hr_expense_data.xml',
    ],
    'installable': True,
    'maintainer': 'ps-tubtim',
}
