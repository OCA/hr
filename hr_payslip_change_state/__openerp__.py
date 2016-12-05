# -*- coding: utf-8 -*-
# © 2016 - Eficent http://www.eficent.com/
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Change the state of many payslips at a time",
    "version": "8.0.1.0.0",
    "license": "AGPL-3",
    "category": "Human Resources",
    "author": "Eficent, Odoo Community Association (OCA)",
    "depends": ['hr_payroll_cancel'],
    "data": [
        "wizard/hr_payslip_change_state_view.xml",
    ],
    "installable": True,
    "auto_install": False,
}
