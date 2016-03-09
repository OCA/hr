# -*- coding: utf-8 -*-
# © 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Employee Infraction Management',
    "version": "8.0.1.0.0",
    'category': 'Generic Modules/Human Resources',
    'author': "OpenSynergy Indonesia,"
              "Michael Telahun Makonnen <mmakonnen@gmail.com>,"
              "Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'security/hr_infraction_security.xml',
        'security/ir.model.access.csv',
        'demo/hr_infraction_demo.xml',
        'datas/hr_infraction_data.xml',
        'views/hr_infraction_views.xml',
        'views/hr_employee_views.xml',
    ],
    'installable': True,
}
