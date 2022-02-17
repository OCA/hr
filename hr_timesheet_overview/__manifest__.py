# Copyright 2021 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": "HR Timesheet Overview",
    "version": "14.0.1.0.0",
    "author": "Camptocamp SA",
    "license": "AGPL-3",
    "category": "",
    "depends": [
        "board",
        "hr",
        "hr_contract",
        "project_timesheet_holidays",
        "hr_timesheet",
        "web_dashboard",
    ],
    "website": "http://www.camptocamp.com",
    "data": [
        "security/ir.model.access.csv",
        "views/menu_views.xml",
        "views/hr_employee_hour_views.xml",
        "report/hr_employee_hour_report_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
}
