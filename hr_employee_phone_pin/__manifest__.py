# Copyright 2024 Binhex (<https://binhex.cloud>)
# Copyright 2024 Binhex Ariel Barreiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Employee Phone PIN",
    "version": "16.0.1.0.0",
    "category": "Human Resources",
    "author": "Binhex, Odoo Community Association (OCA)",
    "maintainers": ["arielbarreiros96"],
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "depends": ["hr"],
    "data": [
        "views/hr_employee_views.xml",
        "security/hr_security.xml",
        "views/hr_employee_public_views.xml",
    ],
    "installable": True,
}
