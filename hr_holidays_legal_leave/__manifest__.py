# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Holidays Legal Leave',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Allows the definition of legal/annual leave',
    'author': 'iDT LABS, '
              'Odoo Community Association (OCA)',
    'website': 'http://idtlabs.sl',
    'depends': ['hr_holidays'],
    'data': [
        'views/hr_holidays_status.xml',
    ],
    'installable': True,
}
