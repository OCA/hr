# -*- coding: utf-8 -*-
{
    'name': "HR Attendance Quagga",
    'summary': """Attendance with Quaggajs""",
    'author': "Netfarm S.r.l",
    'website': "https://github.com/OCA/hr",
    'category': 'Human Resources',
    'version': '10.0.0.0.0',
    'license': 'AGPL-3',
    'depends': ['base', 'hr_attendance'],
    'data': [
        'views/assets.xml',
        'views/views.xml'
    ],
    'qweb': [
        'static/src/xml/template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
