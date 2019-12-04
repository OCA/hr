# -*- coding: utf-8 -*-
# Copyright 2017-2018 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Theoretical vs Attended Time Analysis",
    "version": "10.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
        "hr_holidays_compute_days",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_attendance_report_theoretical_time_security.xml",
        "views/hr_holidays_status_views.xml",
        "views/hr_employee_views.xml",
        "reports/hr_attendance_theoretical_time_report_views.xml",
    ],
}
