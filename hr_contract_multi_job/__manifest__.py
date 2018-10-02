# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'HR Contract Multi Jobs',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Savoir-faire Linux, '
              'Fekete Mihai (Forest and Biomass Services Romania), '
              'Odoo Community Association (OCA)',
    'website': "https://github.com/OCA/hr",
    'depends': [
        'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
    ],
    'installable': True,
}
