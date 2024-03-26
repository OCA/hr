# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Employee Birthday Mail",
    "summary": """
        Automating birthday mail messages and fostering for a positive work environment.""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr", "mail"],
    "data": [
        "data/data.xml",
        "data/ir_cron.xml",
        "views/hr_employee_views.xml",
        "views/res_user_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
