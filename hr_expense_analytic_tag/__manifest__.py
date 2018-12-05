# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Link Analytic Tags with Expense Tracker",
    "version": "11.0.1.0.0",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": [
        'hr_expense',
    ],
    'data': [
        'views/hr_expense_views.xml',
        'views/hr_expense_sheet_views.xml',
    ],
    "installable": True,
}
