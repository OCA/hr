# -*- coding: utf-8 -*-
#   Copyright (C) 2017 EBII (http://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': "HR Accident at work",

    'description': """
        HR Accident at work for OCA""",

    'license': 'AGPL-3',
    'author': "Saaslys, Odoo Community Association (OCA)",
    'website': "https://www.saaslys.com",

    'category': 'Human Resources',
    'version': '10.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        'views/hr_accident_at_work.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
