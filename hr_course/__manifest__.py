# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "HR Course",
    "summary": """
        This module allows your to manage employee's training courses""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["hr", "mail"],
    "data": [
        "security/course_security.xml",
        "security/ir.model.access.csv",
        "views/hr_course_category_views.xml",
        "views/hr_course_views.xml",
        "views/hr_employee_views.xml",
    ],
}
