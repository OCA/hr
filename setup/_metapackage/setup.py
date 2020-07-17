import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-hr_contract_currency',
        'odoo13-addon-hr_contract_multi_job',
        'odoo13-addon-hr_employee_age',
        'odoo13-addon-hr_employee_calendar_planning',
        'odoo13-addon-hr_employee_firstname',
        'odoo13-addon-hr_employee_phone_extension',
        'odoo13-addon-hr_employee_relative',
        'odoo13-addon-hr_employee_service',
        'odoo13-addon-hr_employee_ssn',
        'odoo13-addon-hr_org_chart_overview',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
