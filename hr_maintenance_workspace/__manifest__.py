# Copyright 2023 SDi Digital Group (https://www.sdi.es/odoo-cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Hr Maintenance Workspace",
    "summary": "Allows to assign equipments and employees to workspaces.",
    "version": "14.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "SDi Digital Group, Odoo Community Association (OCA)",
    "maintainers": ["valentincastravete", "JorgeQuinteros"],
    "license": "AGPL-3",
    "depends": ["hr_maintenance"],
    "data": [
        "security/ir.model.access.csv",
        "views/maintenance_views.xml",
        "views/maintenance_workspace_views.xml",
        "views/hr_maintenance_workspace_menu_views.xml",
        "views/hr_employee_views.xml",
    ],
}
