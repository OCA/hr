# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Personal Protective Equipment (PPE) Management",
    "version": "13.0.2.0.0",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago", "eduaparicio"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr_personal_equipment_request"],
    "data": [
        "views/product_template.xml",
        "views/hr_personal_equipment.xml",
        "views/hr_personal_equipment_request.xml",
        "data/hr_employee_ppe_cron.xml",
        "reports/hr_employee_ppe_report_template.xml",
        "reports/hr_employee_ppe_report.xml",
    ],
    "installable": True,
}
