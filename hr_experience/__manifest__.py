# Copyright 2013 Savoir-faire Linux (<http://www.savoirfairelinux.com>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Experience Management",
    "version": "12.0.1.0.0",
    "author": "Savoir-faire Linux,"
              "OpenSynergy Indonesia,"
              "Numigi,"
              "Odoo Community Association (OCA)",
    "website": "https://github.com/oca/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr"],
    "data": [
        "security/hr_security.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "views/hr_academic_view.xml",
        "views/hr_professional_view.xml",
        "views/hr_certification_view.xml",
    ],
    'installable': True
}
