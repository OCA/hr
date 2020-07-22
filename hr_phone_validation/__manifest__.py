{
    'name': 'HR Phone Numbers Validation',
    'summary': 'Validate and format phone numbers for employee',
    'version': '11.0.1.0.0',
    'category': 'Human Resources',
    'author': "Florent de Labarre,"
              "Odoo Community Association (OCA)",
    'website': 'https://github.com/OCA/hr',
    'license': 'AGPL-3',
    'external_dependencies': {
        'python': [
            'phonenumbers',
        ],
    },
    'depends': [
        'phone_validation',
        'hr',
    ],
}
