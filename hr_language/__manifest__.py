# -*- coding: utf-8 -*-
# Copyright (C) 2017-Today: Odoo Community Association (OCA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Language Management",
    "version": "10.0.0.1.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "Savoir-faire Linux, Acsone, Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "depends": [
        "hr",
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/hr_language.xml',
    ],
    "demo": [],
    'installable': True,
}
