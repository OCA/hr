# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Employee spouse",
    "version": "8.0.1.0.0",
    "author": "Therp BV, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "hr",
    "summary": "Specify a partner that is employee's spouse",
    "depends": [
        'hr',
    ],
    "data": [
        'views/hr_employee.xml',
        'data/hr_employee_spouse_data.xml',
    ],
    "installable": True,
}
