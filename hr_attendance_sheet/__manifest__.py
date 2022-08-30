# Copyright 2020 Pavlov Media
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "HR Attendance Sheet",
    "version": "12.0.1.0.0",
    "category": "Human Resources",
    "summary": "Group attendances into attendance sheets.",
    "website": "https://github.com/OCA/hr",
    "author": "Odoo S.A., Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": [
        "hr_attendance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security_groups.xml",
        "data/cron.xml",
        "data/mail_data.xml",
        "report/hr_attendance_sheet_report.xml",
        "views/hr_attendance_sheet.xml",
        "views/hr_attendance_view.xml",
        "views/hr_department.xml",
        "views/hr_employee.xml",
        "views/res_config_settings_views.xml",
        "views/res_company.xml",
    ],
    "development_status": "Beta",
}
