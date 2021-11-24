# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Personal Equipment Request Tier Validation",
    "summary": """
        Enables tier validation from hr.personal.equipment.request""",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "www.creublanca.es",
    "depends": ["hr_personal_equipment_request", "base_tier_validation"],
    "data": ["data/tier_definition.xml"],
    "demo": [],
}
