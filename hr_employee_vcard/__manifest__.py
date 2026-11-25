{
    "name": "HR Employee vCard",
    "version": "18.0.1.0.0",
    "summary": "Manage employee business cards.",
    "author": "Vortex Dimensión Digital, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "LGPL-3",
    "category": "Human Resources",
    "depends": ["hr"],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_vcard_templates.xml",
        "reports/hr_employee_vcard_reports.xml",
        "data/hr_employee_vcard_layout_data.xml",
        "data/hr_employee_vcard_field_data.xml",
        "wizards/hr_employee_vcard_wizard.xml",
        "views/hr_employee_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "hr_employee_vcard/static/src/scss/*.scss",
        ],
    },
    "installable": True,
    "auto_install": False,
    "application": False,
}
