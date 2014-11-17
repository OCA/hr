# -*- coding: utf-8 -*-
{
    'name': 'Duty Roster',
    'version': '0.1',
    'category': 'Human Resources',
    'description': """
Duty Roster
===========

This is a generic module to allow easy management of staff duty roster.
It should be used together with hr_holidays such that leaves application
that spans multiple days takes into account of half/off duty days.
""",
    'author': "CODEKAKI SYSTEMS (R49045/14)",
    'website': 'http://codekaki.com',
    'depends': ['hr'],
    'images': [
        'images/shift_code_tree.png',
        'images/shift_code.png',
        'images/duty_roster.png',
        'images/duty_roster_err.png',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/ir.rule.xml',
        'data/hr_shift_code.xml',
        'data/hr_roster.xml',
        'duty_roster_view.xml',
        'duty_roster_workflow.xml',
    ],
    'css': [
        'static/src/css/hr_roster.css',
    ],
    'js': [
        'static/src/js/hr_roster.js',
    ],
    'qweb': [
        'static/src/xml/hr_shift_code.xml',
        'static/src/xml/hr_roster.xml',
    ],
    'demo': [],
    'test': [],
    'installable': True,
}
