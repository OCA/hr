# SPDX-FileCopyrightText: 2024 Coop IT Easy SC
#
# SPDX-License-Identifier: AGPL-3.0-or-later

{
    "name": "Multi-week calendars",
    "summary": """
        Allow a calendar to alternate between multiple weeks.""",
    "version": "12.0.1.0.0",
    "category": "Hidden",
    "website": "https://github.com/OCA/hr",
    "author": "Coop IT Easy SC, Odoo Community Association (OCA)",
    "maintainers": ["carmenbianca"],
    "license": "AGPL-3",
    "application": False,
    "depends": [
        "resource",
    ],
    "data": [
        "views/resource_calendar_views.xml",
    ],
}
