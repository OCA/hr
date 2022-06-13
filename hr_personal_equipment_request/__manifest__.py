# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Hr Personal Equipment Request",
    "summary": """
        This addon allows to manage employee personal equipment""",
    "version": "15.0.1.0.0",
    "license": "AGPL-3",
    "author": "Creu Blanca,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "depends": ["product", "hr", "mail"],
    "data": [
        "security/hr_personal_equipment_request_security.xml",
        "security/ir.model.access.csv",
        "views/product_template.xml",
        "views/hr_personal_equipment.xml",
        "views/hr_personal_equipment_request.xml",
        "views/hr_employee.xml",
    ],
}
