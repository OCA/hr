import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-hr_branch',
        'odoo14-addon-hr_contract_currency',
        'odoo14-addon-hr_contract_multi_job',
        'odoo14-addon-hr_contract_reference',
        'odoo14-addon-hr_course',
        'odoo14-addon-hr_department_code',
        'odoo14-addon-hr_employee_age',
        'odoo14-addon-hr_employee_birth_name',
        'odoo14-addon-hr_employee_calendar_planning',
        'odoo14-addon-hr_employee_digitized_signature',
        'odoo14-addon-hr_employee_firstname',
        'odoo14-addon-hr_employee_lastnames',
        'odoo14-addon-hr_employee_medical_examination',
        'odoo14-addon-hr_employee_phone_extension',
        'odoo14-addon-hr_employee_relative',
        'odoo14-addon-hr_employee_service',
        'odoo14-addon-hr_employee_ssn',
        'odoo14-addon-hr_org_chart_overview',
        'odoo14-addon-hr_recruitment_notification',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
