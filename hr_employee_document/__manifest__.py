# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Employee Document",
    "version": "17.0.1.0.1",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "Documents attached to the employee profile",
    "depends": ["hr"],
    "data": [
        "views/hr_employee.xml",
        "views/hr_employee_public.xml",
    ],
}
