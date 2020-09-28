# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Expense Receipt Require",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """This module allows you to define expense products that
        requires a receipt to be submitted.""",
    "category": "Human Resources",
    "maintainers": ["Khalid-SerpentCS"],
    "website": "https://github.com/OCA/hr",
    "depends": [
        "hr_expense"
    ],
    "data": [
        "views/hr_expense_views.xml",
    ],
    "auto_install": False,
    "application": False,
    "installable": True,
}
