import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-hr_attendance_report_theoretical_time',
        'odoo12-addon-hr_attendance_rfid',
        'odoo12-addon-hr_contract_currency',
        'odoo12-addon-hr_employee_document',
        'odoo12-addon-hr_employee_health',
        'odoo12-addon-hr_employee_id',
        'odoo12-addon-hr_employee_relative',
        'odoo12-addon-hr_employee_service',
        'odoo12-addon-hr_employee_service_contract',
        'odoo12-addon-hr_employee_social_media',
        'odoo12-addon-hr_employee_ssn',
        'odoo12-addon-hr_experience',
        'odoo12-addon-hr_holidays_leave_auto_approve',
        'odoo12-addon-hr_holidays_length_validation',
        'odoo12-addon-hr_holidays_public',
        'odoo12-addon-hr_holidays_settings',
        'odoo12-addon-hr_payroll_cancel',
        'odoo12-addon-hr_skill',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
