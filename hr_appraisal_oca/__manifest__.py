# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Appraisal Oca",
    "version": "16.0.1.0.0",
    "category": "Human Resources/Employees",
    "website": "https://github.com/OCA/hr",
    "author": "Fundación Esment, Odoo Community Association (OCA)",
    "maintainers": ["ebauza", "pedrobaeza"],
    "images": ["static/description/banner.png"],
    "summary": "Module for managing employee appraisals",
    "license": "AGPL-3",
    "depends": ["base", "hr", "mail"],
    "installable": True,
    "data": [
        "security/hr_appraisal_security.xml",
        "security/ir.model.access.csv",
        "data/mail_template_data.xml",
        "data/mail_activity_type_data.xml",
        "views/hr_appraisal_form_view.xml",
        "views/res_config_settings_views.xml",
        "views/hr_employee_form_view.xml",
        "views/hr_appraisal_template_form_view.xml",
        "views/hr_appraisal_tag_form_view.xml",
        "wizard/hr_appraisal_wizard_form_view.xml",
        "wizard/hr_appraisal_request_wizard_view.xml",
    ],
}
