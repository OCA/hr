# Copyright 2025 Ángel Rivas <angel.rivas@sygel.es>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Hr Collective Agreement Partner",
    "summary": "Partner integration for collective agreements",
    "version": "18.0.1.0.0",
    "author": "Sygel, Odoo Community Association (OCA)",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "depends": ["contacts", "hr_collective_agreement"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/collective_agreement_assign_wizard.xml",
        "views/res_partner_views.xml",
        "views/collective_agreement_views.xml",
    ],
    "license": "LGPL-3",
}
