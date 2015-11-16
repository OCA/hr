# -*- coding: utf-8 -*-
# © 2015 Eficent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR Payslip Report",
    "summary": "HR Payslip Report",
    "version": "7.0.1.0.0",
    "category": "Human Resources",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "hr_payroll",
    ],
    "data": [
        "report/hr_payslip_report_view.xml",
        "security/ir.model.access.csv"
    ],
}
