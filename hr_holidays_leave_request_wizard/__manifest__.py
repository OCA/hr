# Copyright 2018-2019 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Leave Request Wizard',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Leave request wizard and leave request creation/editing form',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_leave.xml',
        'wizards/hr_leave_wizard.xml',
    ],
}
