# © 2016 - Eficent http://www.eficent.com/
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Human Resources Payslip Change State",
    "summary": "Change the state of many payslips at a time",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "category": "Human Resources",
    "author": "Eficent, Odoo Community Association (OCA)",
    "depends": [
        'hr_payroll_cancel'
    ],
    "data": [
        "wizard/hr_payslip_change_state_view.xml",
    ],
    "installable": True,
}
