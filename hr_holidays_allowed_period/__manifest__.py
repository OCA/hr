# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Holiday Allowed Period',
    'summary': """
        This module allows you to set a range to holidays.""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_status_views.xml',
        'views/hr_holidays_views.xml',
    ],
}
