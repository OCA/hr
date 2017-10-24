# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Marital status",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Configurable marital statuses for employees",
    "depends": [
        'hr',
    ],
    "demo": [
        "demo/hr_employee.xml",
    ],
    "data": [
        "views/hr_employee_marital_status.xml",
        "views/hr_employee.xml",
        "data/hr_employee_marital_status.xml",
        'security/ir.model.access.csv',
    ],
    "post_init_hook": 'post_init_hook',
}
