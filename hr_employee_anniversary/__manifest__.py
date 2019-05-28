{
    'name': "Employee's anniversary",

    'summary': """
        Define the anniversary date for employees.
        """,

    'description': """
        Adds a employment anniversary field next to birthday field.
    """,

    'author': "BerrySoft MX, Odoo Community Association (OCA)",
    'website': "https://github.com/OCA/hr",

    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'Generic Modules/Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/hr_employee_views.xml',
    ],
    # only loaded in demonstration mode
}
