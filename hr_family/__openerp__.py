# -*- coding: utf-8 -*-
# Copyright (C) 2011, 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
# Copyright 2016 Camptocamp SA Damien Crier
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Employee Family Information',
    'version': '9.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,"
              "Camptocamp SA,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.openerp.com',
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
