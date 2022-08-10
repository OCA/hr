# Copyright (C) 2022 - TODAY, Open Source Integrators
# Copyright (C) 2022 Serpent Consulting Services
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Gamification Email Notification",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": """Open Source Integrators,
        Serpent Consulting Services,
        Odoo Community Association (OCA)""",
    "summary": """Send Email to all the Employees with all the award given in
     the last week.""",
    "category": "Human Resources",
    "maintainers": ["Hardik-OSI"],
    "website": "https://github.com/OCA/hr",
    "depends": ["hr_gamification", "gamification"],
    "data": ["data/ir_cron_data.xml", "data/mail_template.xml", "views/badge.xml"],
    "qweb": [],
    "auto_install": False,
    "application": False,
    "installable": True,
    "development_status": "Production/Stable",
}
