# -*- coding: utf-8 -*-
#   Copyright (C) 2018 EBII (https://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': "HR Contract Amendment",

    'summary': """
        HR contract Extension
        Amendment Hr contract""",

    'description': """
        HR contract Extension
        Amendment Hr contract""",

    'author': "EBII Saaslys",
    'website': "https://www.saaslys.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '10.0.0.1.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': [
         'views/hr_contract_amendment.xml',
         'views/hr_contract_view.xml',
         'security/ir.model.access.csv',
         'data/sequence.xml',
    ],
    'installable': True,
}




