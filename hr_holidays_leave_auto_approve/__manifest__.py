# Copyright 2016-2019 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Auto Approve Leaves',
    'version': '12.0.2.0.0',
    'license': 'AGPL-3',
    'summary': 'Leave type for auto-validation of Leaves',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'category': 'Human Resources',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_holidays_status.xml',
    ],
    'installable': True,
}
