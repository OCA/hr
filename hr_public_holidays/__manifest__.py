# -*- coding: utf-8 -*-
# ©  2015 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'HR Public Holidays',
    'version': '10.0.1.0.1',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>, "
              "Odoo Community Association (OCA)",
    'summary': "Manage Public Holidays",
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_public_holidays_view.xml',
        'wizards/public_holidays_next_year_wizard.xml',
    ],
    'installable': True,
}
