# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Select Expense Journal",
    "version": "12.0.1.0.0",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "summary": "Set the Journal for the payment type used to pay the expense",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "depends": ["hr_expense"],
    "category": "Human Resources/Expenses",
    "data": [
        "views/hr_expense_views.xml",
    ],
    "installable": True,
    "maintainers": ["dreispt"],
    "development_status": "Beta",
}
