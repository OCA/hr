# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Work Entry Usability",
    "summary": "Improve usability of work entries and work entry types",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "maintainers": ["mihien"],
    "license": "AGPL-3",
    "depends": [
        "hr_work_entry",
    ],
    "data": [
        "views/hr_work_entry_type_views.xml",
        # hr_views depends on items in hr_work_entry_type_views, keep this order
        "views/hr_views.xml",
    ],
}
