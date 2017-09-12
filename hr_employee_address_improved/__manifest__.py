# -*- coding: utf-8 -*-
# Author: Simone Orsi
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'HR Employee Address Improved',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'author': 'Camptocamp,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['hr'],
    'website': 'http://www.camptocamp.com',
    'data': [
        'views/hr.xml',
    ],
    'installable': True,
    'post_init_hook': 'post_init_hook',
}
