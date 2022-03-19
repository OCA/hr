# Copyright (C) 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Expense Type",
    "summary": "Ability to add type in expenses.",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Trey (www.trey.es), Odoo Community Association (OCA)",
    "maintainers": ["cubells"],
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_expense"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_expense_type_views.xml",
        "views/hr_expense_views.xml",
    ],
    "installable": True,
}
