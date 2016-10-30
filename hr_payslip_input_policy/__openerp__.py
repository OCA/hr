# -*- coding: utf-8 -*-
# Copyright 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Payslip Input Type Policy",
    "version": "8.0.1.0.0",
    "category": "Human Resources",
    "website": "https://opensynergy-indonesia/",
    "author": "OpenSynergy Indonesia, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_payroll",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_payslip_input_type_views.xml",
        "views/hr_contract_views.xml",
    ],
}
