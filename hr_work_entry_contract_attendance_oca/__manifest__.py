# SPDX-FileCopyrightText: 2026 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Work Entries from Attendances (OCA)",
    "summary": "Generate work entries from attendances",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "hr_attendance",
        "hr_work_entry_contract",
    ],
    "data": [
        "views/hr_contract_views.xml",
        "views/hr_work_entry_views.xml",
        "views/res_config_settings_views.xml",
    ],
}
