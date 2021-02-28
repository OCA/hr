# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Personal Protective Equipment (PPE) Management",
    "version": "13.0.1.0.0",
    "author": "Escodoo, Odoo Community Association (OCA)",
    "maintainers": ["marcelsavegnago", "eduaparicio"],
    "images": ["static/description/banner.png"],
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr", "mail", "product"],
    "data": [
        "security/hr_security.xml",
        "security/hr_employee_ppe_equipment.xml",
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "views/hr_employee_ppe_view.xml",
        "views/hr_employee_ppe_equipment.xml",
        "data/hr_employee_ppe_cron.xml",
    ],
    "demo": ["demo/hr_employee_ppe_demo.xml"],
    "installable": True,
}
