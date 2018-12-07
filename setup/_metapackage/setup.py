import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-hr",
    description="Meta package for oca-hr Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-hr_attendance_rfid',
        'odoo12-addon-hr_employee_document',
        'odoo12-addon-hr_employee_health',
        'odoo12-addon-hr_employee_id',
        'odoo12-addon-hr_employee_relative',
        'odoo12-addon-hr_employee_service',
        'odoo12-addon-hr_employee_service_contract',
        'odoo12-addon-hr_employee_social_media',
        'odoo12-addon-hr_employee_ssn',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
