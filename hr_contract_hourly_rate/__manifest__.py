# Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR Contract Hourly Rate',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': 'Savoir-faire Linux, '
              'Fekete Mihai (Forest and Biomass Services Romania), '
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr_contract_multi_job',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_hourly_rate_class_view.xml',
    ],
}
