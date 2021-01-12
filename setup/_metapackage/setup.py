import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-hr_branch',
        'odoo13-addon-hr_calendar_rest_time',
        'odoo13-addon-hr_contract_currency',
        'odoo13-addon-hr_contract_multi_job',
        'odoo13-addon-hr_contract_rate',
        'odoo13-addon-hr_contract_reference',
        'odoo13-addon-hr_course',
        'odoo13-addon-hr_employee_age',
        'odoo13-addon-hr_employee_calendar_planning',
        'odoo13-addon-hr_employee_document',
        'odoo13-addon-hr_employee_firstname',
        'odoo13-addon-hr_employee_language',
        'odoo13-addon-hr_employee_lastnames',
        'odoo13-addon-hr_employee_medical_examination',
        'odoo13-addon-hr_employee_phone_extension',
        'odoo13-addon-hr_employee_relative',
        'odoo13-addon-hr_employee_service',
        'odoo13-addon-hr_employee_service_contract',
        'odoo13-addon-hr_employee_ssn',
        'odoo13-addon-hr_job_category',
        'odoo13-addon-hr_org_chart_overview',
        'odoo13-addon-resource_hook',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
