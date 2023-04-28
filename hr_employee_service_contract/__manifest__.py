# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2020 CorporateHub (https://corporatehub.eu)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Employee Service from Contracts",
    "version": "16.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "CorporateHub, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": (
        "Employee service information & duration based on employee's contracts"
    ),
    "depends": ["hr", "hr_contract", "hr_employee_service"],
    "external_dependencies": {"python": ["dateutil"]},
}
