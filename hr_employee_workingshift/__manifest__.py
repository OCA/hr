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

    'category': 'Human Resources',
    'version': '0.1',

    'depends': ['hr'],

    'data': [
        'security/ir.model.access.csv',
        "views/hr_employee_working_shift_view.xml",
    ],

    'installable': True,
}
