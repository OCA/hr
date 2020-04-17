# -*- coding: utf-8 -*-
# Author: Damien Crier
# Copyright 2016 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Imposed holidays days',
    'version': '10.0.1.0.1',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'author': 'Camptocamp SA, '
              'Odoo Community Association (OCA)',
    'website': 'http://www.camptocamp.com',
    'depends': ['hr_holidays'],
    'data': ['views/imposed_days.xml',
             'security/ir.model.access.csv',
             ],
    'installable': True,
}
