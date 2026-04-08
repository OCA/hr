# Copyright 2026 Moduon Team S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0)

{
    "name": "Employee bank restrict",
    "summary": "Restrict employee bank account in employee partner",
    "version": "18.0.1.0.0",
    "development_status": "Alpha",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Moduon, Odoo Community Association (OCA)",
    "maintainers": ["EmilioPascual", "rafaelbn"],
    "license": "LGPL-3",
    "application": False,
    "installable": True,
    "autoinstall": True,
    "depends": [
        "hr",
        "account",
    ],
    "data": [
        "views/res_partner_views.xml",
    ],
}
