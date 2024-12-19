# Copyright 2021 César Fernández Domínguez
# Copyright 2024 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Professional Category",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["hr_contract"],
    "installable": True,
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/hr_professional_category_views.xml",
        "views/hr_contract_views.xml",
    ],
    "demo": ["demo/hr_professional_category_demo.xml"],
    "maintainers": ["victoralmau"],
}
