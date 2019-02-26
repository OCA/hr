# Copyright 2017-2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Theoretical vs Attended Time Analysis",
    "version": "12.0.1.0.1",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
        "hr_holidays_public",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/hr_attendance_report_theoretical_time_security.xml",
        "views/hr_attendance_views.xml",
        "views/hr_leave_type_views.xml",
        "views/hr_employee_views.xml",
        "reports/hr_attendance_theoretical_time_report_views.xml",
    ],
}
