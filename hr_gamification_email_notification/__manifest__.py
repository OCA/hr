# Copyright (C) 2020 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "OSI HR Gamification Extended",
    "version": "12.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators",
    "summary": """Send Email to all the Employees with all the award given in
     the last week.""",
    "category": "Helpdesk",
    "maintainers": ["Khalid-SerpentCS"],
    "website": "http://www.opensourceintegrators.com",
    "depends": ["hr_gamification"],
    "data": ["data/ir_cron_data.xml", "data/badge.xml", "views/badge.xml"],
    "qweb": [],
    "auto_install": False,
    "application": False,
    "installable": True,
}
