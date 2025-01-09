# Copyright 2025 INVITU SARL
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Employee external Partner timesheet",
    "summary": "Include external partners to timesheet views",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "author": "INVITU SARL, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet",
        "hr_employee_partner_external",
    ],
    "data": ["views/hr_timesheet_views.xml"],
}
