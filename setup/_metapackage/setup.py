import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-hr_contract_currency',
        'odoo13-addon-hr_employee_age',
        'odoo13-addon-hr_employee_firstname',
        'odoo13-addon-hr_employee_phone_extension',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
