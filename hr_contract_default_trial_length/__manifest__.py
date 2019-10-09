# -*- coding: utf-8 -*-
# Copyright 2015 Salton Massally
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Default Contract Trail Length",
    "version": "10.0.1.0.0",
    'license': 'AGPL-3',
    'author': "Salton Massally <smassally@idtlabs.sl>, "
               "Odoo Community Association (OCA)",
    "website": "http://idtlabs.sl",
    "category": "Human Resources",
    "summary": "Define default trail length for contracts",
    "depends": [
        'hr_contract'
    ],
    "data": [
        'views/hr_contract_type.xml',
    ],
    'installable': True,
}
