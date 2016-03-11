# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Employee Awards Management",
    "summary": "Manage employee awards",
    "version": "8.0.1.0.0",
    "category": "Generic Modules/Human Resources",
    "website": "https://openynergy-indonesia.com/",
    "author": "OpenSynery Indonesia, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_award_security.xml",
        "data/hr_award_data.xml",
        "demo/hr_award_demo.xml",
        "views/hr_award_views.xml",
        "views/hr_employee_views.xml",
    ],
    "demo": [
    ],
}
