# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Skills Management",
    "summary": "Manage your employee skills",
    "version": "12.0.1.2.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": (
        "Savoir-faire Linux, "
        "Brainbean Apps, "
        "Odoo Community Association (OCA)"
    ),
    "website": "https://github.com/OCA/hr",
    "depends": [
        "hr"
    ],
    'data': [
        "security/ir.model.access.csv",
        "views/hr_skill.xml",
        "views/hr_employee.xml",
        "views/hr_employee_skill.xml",
    ],
    'installable': True,
}
