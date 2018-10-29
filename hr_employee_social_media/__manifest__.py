# Copyright 2017 Denis Leemann, Camptocamp SA
# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Employee Social Media',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'author':
        'Brainbean Apps, '
        'Camptocamp SA, '
        'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/social_media.xml',
        'views/hr_employee_view.xml',
        'views/hr_social_media.xml',
    ],
    'installable': True,
    'auto_install': False,
}
