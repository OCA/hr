# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "User and partner data from employee",
    "version": "8.0.1.0.1",
    "author": "Odoo Community Association (OCA),Therp BV",
    "license": "AGPL-3",
    "category": "Human Resources",
    "summary": "Update user's and partner's data fields from employee record",
    "depends": [
        'hr',
    ],
    "data": [
        "data/res_partner_category.xml",
        'views/hr_employee.xml',
        'views/res_users.xml',
    ],
    "test": [
    ],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "auto_install": False,
    "installable": True,
    "application": False,
    "external_dependencies": {
        'python': [],
    },
}
