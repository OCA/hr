# -*- coding: utf-8 -*-
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Supplier invoices on HR expenses',
    'version': '10.0.1.0.1',
    'category': 'Human Resources',
    'author': 'Tecnativa, '
              'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'website': 'https://www.tecnativa.com',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'views/hr_expense_views.xml',
    ],
    'installable': True,
}
