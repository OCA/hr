# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Birth Data",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["MiquelRForgeFlow"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Adds birth time and birth coordinates to the employee profile",
    "depends": ["hr"],
    "data": [
        "views/hr_employee_views.xml",
    ],
}
