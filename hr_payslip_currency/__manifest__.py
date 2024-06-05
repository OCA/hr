# Copyright 2024 Newlogic (https://newlogic.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "HR Payslip Currency",
    "version": "17.0.1.0.0",
    "category": "Human Resources",
    "website": "https://github.com/OCA/hr",
    "author": "Newlogic, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "summary": "Employee's contract currency on the payslip",
    "depends": ["hr_contract_currency", "hr_payroll"],
    "data": ["views/report_payslip_templates.xml"],
}
