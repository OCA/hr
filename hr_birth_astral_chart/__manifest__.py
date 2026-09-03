# Copyright 2026 Forgeflow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "HR Birth Astral Chart",
    "version": "19.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["MiquelRForgeFlow"],
    "license": "AGPL-3",
    "installable": True,
    "application": False,
    "summary": "View your full astrological birth chart from your employee profile",
    "external_dependencies": {"python": ["pyswisseph"]},
    "depends": ["hr_birth_data"],
    "data": [
        "views/hr_employee_views.xml",
        "views/res_users_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "hr_birth_astral_chart/static/src/xml/birth_chart_table.xml",
            "hr_birth_astral_chart/static/src/js/birth_chart_table.esm.js",
            "hr_birth_astral_chart/static/src/js/daily_horoscope_service.esm.js",
        ],
    },
}
