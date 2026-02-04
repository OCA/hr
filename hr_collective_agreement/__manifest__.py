# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hr Collective Agreement",
    "summary": "Create and manage collective agreements",
    "version": "18.0.1.0.0",
    "author": "Sygel, Odoo Community Association (OCA)",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_contract"],
    "data": [
        "security/ir.model.access.csv",
        "views/collective_agreement_views.xml",
        "views/collective_agreement_scope_views.xml",
        "views/collective_agreement_publication_views.xml",
    ],
    "license": "LGPL-3",
}
