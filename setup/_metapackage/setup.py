import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-hr_employee_birth_name',
        'odoo11-addon-hr_employee_firstname',
        'odoo11-addon-hr_experience',
        'odoo11-addon-hr_holidays_imposed_days',
        'odoo11-addon-hr_holidays_leave_auto_approve',
        'odoo11-addon-hr_holidays_notify_employee_manager',
        'odoo11-addon-hr_holidays_settings',
        'odoo11-addon-hr_payroll_cancel',
        'odoo11-addon-hr_skill',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
