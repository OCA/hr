# Copyright 2016-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'HR Holidays leave repeated',
    'summary': 'Define periodical leaves',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr/',
    'category': 'Human Resources',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_leave_type.xml',
        'views/hr_leave.xml',
    ],
    'installable': True,
}
