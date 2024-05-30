# Copyright (C) 2024 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Employee Group Overview Readonly",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, " "Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/hr",
    "category": "Accounting",
    "depends": [
        "hr_contract",
        "hr_holidays_attendance",
        "hr_fleet",
        "hr_skills",
        "hr_work_entry",
        "hr_gamification",
        "website_slides",
    ],
    "data": [
        "security/hr_employee_security.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
    ],
    "installable": True,
}
