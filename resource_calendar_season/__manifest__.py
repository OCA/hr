# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Resource Calendar Season",
    "summary": "Recurring seasonal working times for a resource calendar",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "category": "Human Resources",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["resource"],
    "data": [
        "security/ir.model.access.csv",
        "views/resource_calendar_views.xml",
    ],
}
