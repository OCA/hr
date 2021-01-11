# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Employee Advance and Clearing',
    'version': '12.0.1.3.0',
    'category': 'Human Resources',
    'author': 'Ecosoft, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'data/advance_product.xml',
        'views/hr_expense_views.xml',
    ],
    'installable': True,
    'maintainers': ['kittiu'],
}
