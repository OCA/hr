# Copyright 2019 Tecnativa - Ernesto Tejeda
# Copyright 2019 Tecnativa - Manuel Calero
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Hr expense cancel",
    "version": "13.0.1.0.2",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr_expense"],
    "data": ["views/hr_expense_views.xml"],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
