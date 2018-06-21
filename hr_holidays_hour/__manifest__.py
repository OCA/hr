# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Leave Management in hours',
    'summary': 'Holidays, Allocation and Leave Requests in Hours',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'category': 'Human Resources',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_holidays.xml',
        'views/hr_holidays_status.xml',
        'report/hr_holidays_report_view.xml',
    ],
    'installable': True,
}
