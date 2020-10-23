# -*- coding: utf-8 -*-
{
    'name': "HR department code",

    'summary': """
        Add function
        1. add code to department
    """,

    'description': """""",

    'author': "Supakorn Kimhajan",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr'],

    # always loaded
    'data': [
        "views/hr_department_code_view.xml",
    ],
    # only loaded in demonstration mode

    'installable': True,
}
