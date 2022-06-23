import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-hr_course>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_firstname>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_lastnames>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_medical_examination>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_partner_external>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_relative>=15.0dev,<15.1dev',
        'odoo-addon-hr_employee_service>=15.0dev,<15.1dev',
        'odoo-addon-hr_personal_equipment_request>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
