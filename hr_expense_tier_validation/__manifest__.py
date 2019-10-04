# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Expense Tier Validation',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'author': 'Ecosoft, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_expense',
        'base_tier_validation',
    ],
    'data': [
        'views/hr_expense_sheet_view.xml',
    ],
    'installable': True,
    'maintainers': ['ps-tubtim'],
}
