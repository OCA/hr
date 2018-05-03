# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# © 2018 Sunflower IT (http://sunflowerweb.nl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Skill Management",
    "version": "8.0.1.3.0",
    "category": "Human Resources",
    "license": "AGPL-3",
    "author": "Savoir-faire Linux,Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "depends": ["hr"],
    "demo": [
        "data/demo.xml",
    ],
    "data": [
        "security/hr_security.xml",
        "security/ir.model.access.csv",
        "views/hr_skill.xml",
        "views/hr_employee.xml",
    ],
    "installable": True,
}
