# -*- encoding: utf-8 -*-
{
    "name" : "Employee Payroll Allowance",
    "version" : "1.0",
    "depends" : ["hr_payroll", "hr_employee_service_length"],
    'author': "Salton Massally <smassally@idtlabs.sl>, "
               "Odoo Community Association (OCA)",
    'category': 'Human Resources',
    "summary": "Allows us to easily create payroll allowance",
    "data" : [
        "views/hr_payroll_allowance.xml",
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
