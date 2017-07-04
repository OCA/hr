# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Employee identification",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Record more data about employees' identity documents",
    "depends": [
        'hr',
    ],
    "data": [
        "data/hr_employee_identification_type.xml",
        "views/hr_employee_identification_type.xml",
        "views/hr_employee.xml",
        'security/ir.model.access.csv',
    ],
}
