# Copyright 2015 iDT LABS (http://www.@idtlabs.sl)
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Extended Leave Days Computation',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Allows to take into account in leave days '
               'computation rest days or full days',
    'author': 'iDT LABS, '
              'Tecnativa, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_status_views.xml',
        'views/hr_holidays_views.xml',
    ],
    'installable': True,
    'pre_init_hook': 'pre_init_hook',
}
