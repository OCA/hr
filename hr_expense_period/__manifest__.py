# Copyright 2023 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Expense Period",
    "summary": "Glue module between expenses and hr period",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow S.L., Odoo Community Association (OCA)",
    "maintainers": ["AaronHForgeFlow"],
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_expense", "hr_period"],
    "data": [
        "views/hr_expense_views.xml",
    ],
    "installable": True,
}
