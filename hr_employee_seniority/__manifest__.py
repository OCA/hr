# -*- coding: utf-8 -*-
# copyright 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# copyright 2017 Denis Leemann, Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Employee Seniority',
    'summary': 'Keep Track of Length of Employment',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>, "
              "Camptocamp SA, "
              "Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
        'hr_contract',
    ],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'views/employee_views.xml',
    ],
    'test': [
    ],
    'installable': True,
}
