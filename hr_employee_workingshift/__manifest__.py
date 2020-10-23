# -*- coding: utf-8 -*-
{
    'name': "HR employee shift",

    'summary': """
        Add function
        1. HR employee shift
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
        'security/ir.model.access.csv',
        "views/hr_employee_working_shift_view.xml",
    ],
    # only loaded in demonstration mode

    'installable': True,
}
