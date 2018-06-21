# Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Employee Family Information',
    'version': '11.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,"
              "Odoo Community Association (OCA)",
    'website': "https://github.com/oca/hr",
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_children.xml',
        'views/hr_employee.xml',
    ],
    'installable': True,
}
