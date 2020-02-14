# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Department Channel',
    'summary': """
        Create Channels from department""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'depends': [
        'hr',
        'mail',
    ],
    'data': [
        'wizards/wizard_create_department_channel.xml',
        'views/hr_department.xml',
    ],
}
