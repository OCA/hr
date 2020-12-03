# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Expense Sale Invoice",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """This module adds smart button on invoice for expenses.""",
    "category": "Human Resources",
    "maintainers": ["Khalid-SerpentCS"],
    "website": "https://github.com/OCA/hr",
    "depends": ["sale_expense"],
    "data": ["views/hr_expense_view.xml", "views/account_invoice_views.xml"],
    "auto_install": False,
    "application": False,
    "installable": True,
}
