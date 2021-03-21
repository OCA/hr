import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-hr_branch',
        'odoo14-addon-hr_contract_reference',
        'odoo14-addon-hr_employee_age',
        'odoo14-addon-hr_employee_firstname',
        'odoo14-addon-hr_employee_lastnames',
        'odoo14-addon-hr_employee_medical_examination',
        'odoo14-addon-hr_employee_phone_extension',
        'odoo14-addon-hr_employee_relative',
        'odoo14-addon-hr_employee_service',
        'odoo14-addon-hr_employee_ssn',
        'odoo14-addon-hr_org_chart_overview',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
