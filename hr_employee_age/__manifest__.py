# Copyright (C) 2015 Salton Massally.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Employee Age",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': "Salton Massally <smassally@idtlabs.sl>, "
            "Odoo Community Association (OCA)",
    "website": "http://idtlabs.sl",
    "category": "Human Resources",
    "summary": "Age field for employee",
    "depends": [
        "hr",
    ],
    "data": [
        'views/hr_employee.xml',
    ],
    'installable': True,
}
