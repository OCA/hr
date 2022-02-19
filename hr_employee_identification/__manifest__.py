# Copyright 2017 Therp BV <https://therp.nl>
# Copyright 2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Employee identification",
    "version": "13.0.1.0.0",
    "author": "Therp BV,Onestein,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Record more data about employee's identity documents",
    "depends": ["hr"],
    "data": [
        "data/hr_employee_identification_type.xml",
        "views/hr_employee_identification_type.xml",
        "views/hr_employee.xml",
        "views/res_users.xml",
        "security/ir.model.access.csv",
    ],
}
