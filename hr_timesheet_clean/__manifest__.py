# Copyright 2024 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "HR Timesheet clean",
    "summary": "HR timesheet clean",
    "author": "ACSONE SA/NV, " "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "category": "Human Resources/Time Off",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "hr_timesheet",
    ],
    "data": [
        "security/timesheet_clean.xml",
        "wizards/timesheet_clean.xml",
    ],
    "installable": True,
}
