{
    'name': 'Employee Benefit',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
        'hr_salary_rule_reference',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_contract_view.xml',
        'views/hr_employee_benefit_category_view.xml',
        'views/hr_employee_benefit_rate_view.xml',
        'views/hr_payslip_view.xml',
        'views/hr_salary_rule_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
