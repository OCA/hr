# -*- coding: utf-8 -*-
# Copyright 2017 Elico Corp (www.elico-corp.com).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Payroll Report",
    "version": "9.0.0.1.0",
    "category": "Generic Modules/Human Resources",
    "website": "https://odoo-community.org/",
    "author": "Elico Corp (www.elico-corp.com), "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_payroll",
    ],
    'data': [
        'views/hr_payroll_report_menu.xml',
        'views/hr_payslip_line_view.xml',
    ],
}
