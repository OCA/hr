# Copyright 2015-2020 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Supplier invoices on HR expenses',
    'version': '12.0.1.3.3',
    'category': 'Human Resources',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'views/hr_expense_views.xml',
        'wizard/expense_create_invoice.xml',
    ],
    'installable': True,
}
