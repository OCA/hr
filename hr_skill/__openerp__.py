# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Skill Management",
    "version": "9.0.1.0.0",
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
