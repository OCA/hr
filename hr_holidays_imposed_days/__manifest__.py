# Author: Damien Crier
# Copyright 2016-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Imposed holidays days',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA, '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': ['hr_holidays'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_holidays_imposed_view.xml',
    ],
    'installable': True,
}
