# -*- coding: utf-8 -*-
#   Copyright (C) 2018 EBII (https://www.saaslys.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': "HR Contract Amendment",

    'summary': """
        HR contract Extension
        Amendment Hr contract""",
    'author': "EBII Saaslys, Odoo Community Association (OCA)",
    'website': "https://www.saaslys.com",
    'category': 'Human Resources',
    'version': '10.0.0.1.0',
    'license': 'AGPL-3',
    # any module necessary for this one to work correctly
    'depends': ['hr_contract'],

    # always loaded
    'data': ['views/hr_contract_amendment.xml',
             'views/hr_contract_view.xml',
             'security/ir.model.access.csv',
             'data/sequence.xml',
             ],
    'installable': True,
}
