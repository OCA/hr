# -*- coding: utf-8 -*-
# © 2015 Eficent
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR Payslip Account Report HR Period",
    "summary": "Adds the HR Period to the Payslip Account Report",
    "version": "7.0.1.0.0",
    "category": "Human Resources",
    "website": "https://odoo-community.org/",
    "author": "Eficent, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {
        "python": [],
        "bin": [],
    },
    "depends": [
        "hr_payslip_account_report",
        "hr_period"
    ],
    "data": [
        "report/hr_payslip_account_report_view.xml",
    ],
    "demo": [
    ],
}
