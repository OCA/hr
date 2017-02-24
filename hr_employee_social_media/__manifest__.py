# -*- coding: utf-8 -*-
# ©  2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Employee Social Media',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'author': "Camptocamp SA, Odoo Community Association (OCA)",
    'website': 'http://www.camptocamp.com',
    'license': 'AGPL-3',
    'depends': ['hr', ],
    'data': [
        # data
        'data/social_media.xml',
        # security
        'security/ir.model.access.csv',
        # views
        'views/hr_employee_view.xml',
        'views/hr_social_media.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
