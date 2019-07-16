# -*- coding: utf-8 -*-
# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Employee Compute Leave Days',
    'version': '10.0.3.1.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Computes the actual leave days '
               'considering rest days and public holidays',
    'author': 'iDT LABS, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_public_holidays',
    ],
    'data': [
        'views/hr_holidays_status_views.xml',
        'views/hr_holidays_views.xml',
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
