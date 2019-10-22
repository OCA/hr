import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-hr_attendance_autoclose',
        'odoo12-addon-hr_attendance_modification_tracking',
        'odoo12-addon-hr_attendance_reason',
        'odoo12-addon-hr_attendance_report_theoretical_time',
        'odoo12-addon-hr_attendance_rfid',
        'odoo12-addon-hr_contract_currency',
        'odoo12-addon-hr_contract_multi_job',
        'odoo12-addon-hr_employee_birth_name',
        'odoo12-addon-hr_employee_calendar_planning',
        'odoo12-addon-hr_employee_display_own_info',
        'odoo12-addon-hr_employee_document',
        'odoo12-addon-hr_employee_firstname',
        'odoo12-addon-hr_employee_health',
        'odoo12-addon-hr_employee_id',
        'odoo12-addon-hr_employee_phone_extension',
        'odoo12-addon-hr_employee_relative',
        'odoo12-addon-hr_employee_service',
        'odoo12-addon-hr_employee_service_contract',
        'odoo12-addon-hr_employee_social_media',
        'odoo12-addon-hr_employee_ssn',
        'odoo12-addon-hr_expense_advance_clearing',
        'odoo12-addon-hr_expense_cancel',
        'odoo12-addon-hr_expense_invoice',
        'odoo12-addon-hr_experience',
        'odoo12-addon-hr_holidays_accrual_advanced',
        'odoo12-addon-hr_holidays_credit',
        'odoo12-addon-hr_holidays_leave_auto_approve',
        'odoo12-addon-hr_holidays_leave_repeated',
        'odoo12-addon-hr_holidays_leave_request_wizard',
        'odoo12-addon-hr_holidays_length_validation',
        'odoo12-addon-hr_holidays_notify_employee_manager',
        'odoo12-addon-hr_holidays_public',
        'odoo12-addon-hr_holidays_settings',
        'odoo12-addon-hr_job_category',
        'odoo12-addon-hr_payroll_cancel',
        'odoo12-addon-hr_period',
        'odoo12-addon-hr_skill',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
