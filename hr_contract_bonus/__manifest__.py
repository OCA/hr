# Copyright 2025 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "HR Contract Bonus",
    "summary": "Manage bonuses in employee contracts",
    "version": "17.0.1.0.0",
    "category": "HR",
    "website": "https://github.com/OCA/hr",
    "author": "APSL-Nagarro, Odoo Community Association (OCA)",
    "maintainers": ["peluko00"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_contract_bonus_views.xml",
        "views/hr_contract_views.xml",
    ],
}
