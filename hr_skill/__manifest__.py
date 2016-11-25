# -*- coding: utf-8 -*-
# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Skill Management",
    "version": "10.0.1.0.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "depends": ["hr"],
    'data': [
        "views/hr_skill.xml",
        "views/hr_employee.xml",
        "security/ir.model.access.csv",
    ],
    'installable': True,
}
