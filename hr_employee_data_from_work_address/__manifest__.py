# -*- coding: utf-8 -*-
# Copyright 2015 Therp BV <http://therp.nl>
{
    "name": "User and partner data from employee",
    "version": "10.0.1.0.0",
    "author": "Odoo Community Association (OCA),Therp BV",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/hr",
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
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    'installable': True,
}
