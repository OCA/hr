# -*- coding: utf-8 -*-
# © 2016 - Eficent http://www.eficent.com/
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    'name': 'Change the state of payslip in tree view',
    'version': '1.0',
    'category': 'Human Resources',
    'description': '''
Change the state of selected payslips in list view
''',
    'author': "Eficent",
    'website': 'http://www.eficent.com',
    'depends': ['hr_payroll_cancel'],
    "demo": [],
    "data": [
        "wizard/hr_payslip_change_state_view.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
