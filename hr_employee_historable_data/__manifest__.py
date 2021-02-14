# Copyright 2021 Iryna Vyshnevska (Camptocamp)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Employee Historable Data",
    "summary": "Allows storing information about employee's documents start/aen date",
    "version": "12.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Camptocamp, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "depends": [
        "hr",
        "hr_contract",
        "date_range",
    ],
    "data": [
        "data/ir_cron.xml",
        "views/utility.xml",
        "views/hr_contract.xml",
        "views/hr_employee.xml",
        "security/ir.model.access.csv",
    ],
}
