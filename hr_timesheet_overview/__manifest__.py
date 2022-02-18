# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Timesheet Overview",
    "version": "14.0.1.0.0",
    "author": "Camptocamp SA, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "",
    "depends": [
        "analytic",
        "board",
        "hr",
        "hr_contract",
        "project_timesheet_holidays",
        "hr_timesheet",
    ],
    "website": "https://github.com/OCA/hr",
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_hour_views.xml",
        "views/hr_employee_hour_report_views.xml",
        "views/hr_contract_view.xml",
        "views/hr_employee_view.xml",
        "views/menu_views.xml",
        "data/ir_cron.xml",
    ],
    "installable": True,
}
