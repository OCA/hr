# -*- coding: utf-8 -*-
# Copyright 2014 - Vauxoo http://www.vauxoo.com/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Hr Payroll Cancel",
    "version": "8.0.1.0.0",
    "author": "Vauxoo,"
              "Odoo Community Association (OCA)",
    "category": "HR",
    "website": "http://www.vauxoo.com/",
    "license": "AGPL-3",
    "depends": [
        "hr_payroll"
    ],
    "data": [
        "hr_payslip_view.xml",
        "hr_payslip_workflow.xml",
    ],
    "installable": True,
    "auto_install": False,
    "post_init_hook": 'post_init_hook',
}
