# Copyright (C) 2024 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Holidays Team Manager",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, " "Odoo Community Association (OCA)",
    "maintainer": "Open Source Integrators",
    "website": "https://github.com/OCA/hr",
    "category": "HR",
    "depends": ["hr_holidays"],
    "data": [
        "data/hr_holidays_rules.xml",
        "data/hr_holidays_security.xml",
        "views/hr_leave_allocation_views.xml",
    ],
    "installable": True,
}
