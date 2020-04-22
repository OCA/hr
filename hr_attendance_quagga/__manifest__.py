# Copyright 2020 Netfarm S.r.l.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    'name': "HR Attendance Quagga",
    'summary': """Attendance with Quaggajs""",
    'description': """
        Attendance with Quaggajs
    """,
    'author': "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/hr',
    'category': 'Human Resources',
    'version': '12.0',
    'depends': ['base', 'hr_attendance'],
    'data': [
        'views/assets.xml'
    ],
    'qweb': [
        'static/src/xml/template.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
