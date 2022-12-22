# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Employee Medical Examination",
    "summary": """
        Adds information about employee's medical examinations""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr"],
    "data": [
        "views/hr_employee_medical_examination_views.xml",
        "wizards/wizard_generate_medical_examination.xml",
        "views/hr_employee_views.xml",
        "security/ir.model.access.csv",
        "security/hr_employee_medical_examination_security.xml",
    ],
}
