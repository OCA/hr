# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Employee data from work address NL names extension",
    "version": "8.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "",
    "summary": "",
    "depends": [
        'hr_employee_data_from_work_address',
        'l10n_nl_hr_employee_name'
    ],
    "data": [
        'views/templates.xml',
        'security/ir.model.access.csv',
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
}
