# -*- coding: utf-8 -*-
# Copyright © 2017 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "HR - Personal protective equipment",
    "version": "8.0.1.0.0",
    "category": "Generic Modules/Human Resources",
    "license": "AGPL-3",
    "author": "AvanzOSC, "
              "Odoo Community Association (OCA)",
    "website": "http://www.avanzosc.es",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Ana Juaristi <anajuaristi@avanzosc.es>",
    ],
    "depends": [
        "hr",
        "stock",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/hr_ppe_data.xml",
        "wizard/hr_employee_partner_selection_view.xml",
        "views/product_view.xml",
        "views/hr_view.xml",
        "views/hr_employee_view.xml",
        "views/hr_job_view.xml",
    ],
    "installable": True,
}
