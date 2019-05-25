# Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': "HR holidays validity date",

    'summary': """
        Allow to define start and end date on holidays type.""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/hr",
    'category': 'Human Resources',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_view.xml',
    ],
}
