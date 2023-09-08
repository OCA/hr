{
    "name": "HR - Payroll Document",
    "summary": "Manage payroll for each employee",
    "author": "APSL, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/hr",
    "license": "AGPL-3",
    "category": "Payrolls",
    "version": "16.0.1.0.0",
    "depends": ["hr", "base_vat"],
    "maintainers": ["peluko00"],
    "external_dependencies": {"python": ["pypdf"]},
    "data": [
        "wizard/payroll_management_wizard.xml",
        "security/ir.model.access.csv",
        "data/email_payroll_employee.xml",
    ],
}
