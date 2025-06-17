# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR Employee Language",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "Savoir-faire Linux, Acsone, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee.xml",
        "views/hr_employee_language.xml",
    ],
    "installable": True,
}
