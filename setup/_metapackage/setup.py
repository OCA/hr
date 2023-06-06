import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-hr_course>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_age>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_digitized_signature>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_firstname>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_lastnames>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_medical_examination>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_partner_external>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_phone_extension>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_relative>=16.0dev,<16.1dev',
        'odoo-addon-hr_employee_ssn>=16.0dev,<16.1dev',
        'odoo-addon-hr_holidays_settings>=16.0dev,<16.1dev',
        'odoo-addon-hr_personal_equipment_request>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
