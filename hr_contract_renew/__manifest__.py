# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hr Contract Renew",
    "summary": """Generate a new contract using an existing contract as a base""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": [
        "hr_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/hr_contract_renew_wizard.xml",
        "views/hr_contract_view.xml",
    ],
    "demo": [],
}
