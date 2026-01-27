# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Time Off Work Entries Usability",
    "summary": "Improve usability of time off work entries",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "hr_work_entry_usability",
        "hr_work_entry_holidays",
    ],
    "data": [
        "views/hr_work_entry_type_views.xml",
        "views/hr_work_entry_views.xml",
    ],
}
