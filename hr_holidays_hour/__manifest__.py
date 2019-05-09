# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    'name': 'Leave Management in hours',
    'summary': 'Leave Allocation and Requests in Hours',
    'author': 'Onestein, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'category': 'Human Resources',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_employee.xml',
        'report/hr_leave_report.xml',
    ],
    'installable': True,
}
