# Copyright 2023 Punt Sistemes (https://puntsistemes.es)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Employee Service from Discontinuous Contracts",
    "version": "15.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "PuntSistemes, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": (
        "Employee service information & duration based on employee's discontinuous contracts"
    ),
    "depends": ["hr_employee_service_contract"],
    "external_dependencies": {"python": ["dateutil"]},
    "data": ["views/hr_contract.xml"],
}
