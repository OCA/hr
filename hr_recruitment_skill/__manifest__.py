# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR recruitment skill',
    'summary': 'Add skills on job position',
    'description': 'Add required and desired skills on job position',
    'version': '10.0.1.0.0',
    'category': 'HR',
    'author': 'Camptocamp SA,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'depends': ['hr_skill',
                'hr_recruitment',
                'hr'
                ],
    'website': 'http://www.camptocamp.com',
    'data': ['views/hr_recruitment_skill.xml'],
    'installable': True,
}
