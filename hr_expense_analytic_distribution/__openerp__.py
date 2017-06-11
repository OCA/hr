# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>.
# Copyright 2017 Vicent Cubells - <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Analytic distributions in expenses",
    "version": "9.0.1.0.0",
    "author": "Therp BV, "
              "Tecnativa,  "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Use analytic plans in expenses",
    "depends": [
        'hr_expense',
        'account_analytic_distribution',
    ],
    "data": [
        "views/hr_expense.xml",
    ],
    "auto_install": False,
    'installable': True,
}
