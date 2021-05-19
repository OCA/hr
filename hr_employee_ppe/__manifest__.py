# Copyright 2020 Escodoo
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Personal Protective Equipment (PPE) Management",
    "version": "12.0.1.1.0",
    "author": "Escodoo, Odoo Community Association (OCA)",
    'maintainers': ['marcelsavegnago', 'eduaparicio'],
    'images': ['static/description/banner.png'],
    "website": "https://github.com/oca/hr",
    "license": "AGPL-3",
    "category": "Human Resources",
    "depends": ["hr",
                'mail',
                'product'],
    "data": [
        "security/hr_security.xml",
        'security/hr_employee_ppe_equipment.xml',
        "security/ir.model.access.csv",
        "views/hr_employee_view.xml",
        "views/hr_employee_ppe_view.xml",
        'views/hr_employee_ppe_equipment.xml',
        'data/hr_employee_ppe_cron.xml',
        'reports/hr_employee_ppe_report_template.xml',
        'reports/hr_employee_ppe_report.xml'
    ],
    'demo': [
        'demo/hr_employee_ppe_demo.xml',
    ],
    'installable': True
}
