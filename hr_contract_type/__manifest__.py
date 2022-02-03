# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Contract Type",
    "summary": """
        Add a Type for Contracts""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_contract"],
    "maintainers": ["etobella"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_contract_type.xml",
        "views/hr_contract.xml",
    ],
    "post_init_hook": "post_init_hook",
}
