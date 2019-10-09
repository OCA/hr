# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Employee citizenship",
    "summary": "Add citizenship field to employee and applicant",
    "version": "10.0.1.0.0",
    "category": "Generic Modules/Human Resources",
    "website": "https://github.com/OCA/hr/",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "hr_recruitment",
    ],
    "data": [
        "views/hr_applicant.xml",
        "views/hr_employee.xml",
        "security/res_groups.xml",
        "security/ir.model.access.csv",
    ],
}
