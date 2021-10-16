import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-hr_contract_reference',
        'odoo9-addon-hr_emergency_contact',
        'odoo9-addon-hr_employee_firstname',
        'odoo9-addon-hr_employee_reference',
        'odoo9-addon-hr_expense_analytic_distribution',
        'odoo9-addon-hr_family',
        'odoo9-addon-hr_holiday_notify_employee_manager',
        'odoo9-addon-hr_holidays_compute_days',
        'odoo9-addon-hr_holidays_leave_auto_approve',
        'odoo9-addon-hr_holidays_legal_leave',
        'odoo9-addon-hr_payroll_cancel',
        'odoo9-addon-hr_payroll_report',
        'odoo9-addon-hr_payslip_change_state',
        'odoo9-addon-hr_public_holidays',
        'odoo9-addon-hr_skill',
        'odoo9-addon-hr_worked_days_from_timesheet',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 9.0',
    ]
)
