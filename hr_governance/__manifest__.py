# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "HR Governance",
    "version": "18.0.1.0.0",
    "author": "Camptocamp, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Generic",
    "website": "https://github.com/OCA/hr",
    "depends": [
        "hr",
        # oca/server-tools:
        "base_m2m_custom_field",
    ],
    "data": [
        "data/role_type_data.xml",
        "data/ir_config_parameter_data.xml",
        "data/governance_circle_data.xml",
        "security/governance_security.xml",
        "security/ir.model.access.csv",
        "views/governance_circle_member_views.xml",
        "views/governance_role_type_views.xml",
        "views/governance_circle_views.xml",
        "views/mail_activity_views.xml",
        "views/menu_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "hr_governance.chart_libs": [
            "/hr_governance/static/lib/**/*",
        ],
        "web.assets_backend": [
            "hr_governance/static/src/components/**/*",
            "hr_governance/static/src/**/*",
        ],
    },
    "installable": True,
    "post_init_hook": "post_init_hook",
}
