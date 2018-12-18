# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Skills Management",
    "summary": "Manage your employee skills",
    "version": "11.0.2.1.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr"],
    'data': [
        "views/hr_skill.xml",
        "views/hr_employee.xml",
        "views/hr_employee_skill.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
}
