# -*- coding: utf-8 -*-
# © 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Experience Management",
    "version": "8.0.1.1.0",
    "author": "Savoir-faire Linux,"
              "OpenSynergy Indonesia,"
              "Odoo Community Association (OCA)",
    "website": "http://www.savoirfairelinux.com",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr", ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_security.xml",
        "views/hr_employee_view.xml",
        "views/hr_academic_view.xml",
        "views/hr_professional_view.xml",
        "views/hr_certification_view.xml",
    ],
    "installable": True
}
