# -*- coding: utf-8 -*-
# Copyright 2015-2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': "HR holidays previous type",

    'summary': """
        Define previous type on holidays type""",
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': "http://acsone.eu",
    'category': 'Human Resources',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays_validity_date',
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_view.xml',
    ],
}
