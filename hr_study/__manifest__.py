# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Employees study field",
    "summary": "Structured study field for employees",
    "version": "15.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/hr_employee_view.xml",
        "views/hr_study_views.xml",
    ],
    "demo": ["demo/hr_study.xml"],
    "installable": True,
    "maintainers": ["victoralmau"],
}
