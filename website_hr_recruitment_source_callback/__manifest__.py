# -*- coding:utf-8 -*-
{
    'name': 'website_hr_recruitment_source_callback',
    'version': '10.0.1.0.0.',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
""",
    'author': "Camptocamp, Odoo Community Association (OCA)",
    'website': 'https://github.com/oca/hr',
    'depends': [
        'website_hr_recruitment',
    ],
    'data': [
        'views/website_hr_recruitment_templates.xml',
        'views/utm_source.xml',
    ],
    'installable': True,
}
