# Copyright 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# Copyright 2016 OpenSynergy Indonesia
# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Employee ID',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author':
        'Brainbean Apps, '
        'Michael Telahun Makonnen, '
        'OpenSynergy Indonesia, '
        'Camptocamp, '
        'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr'
    ],
    'data': [
        'data/hr_employee_sequence.xml',
        'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
