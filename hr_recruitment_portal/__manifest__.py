# Copyright (C) 2020 - TODAY, Marcel Savegnago - Escodoo).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


{
    'name': 'HR Recruitment Portal',
    'summary': """
        This module enables applicants on portal""",
    'version': '12.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'author': 'Escodoo, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/hr',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'portal',
        'hr_recruitment'
    ],
    'data': [
        'security/hr_applicant_portal_security.xml',
        'security/ir.model.access.csv',
        'views/hr_applicant_portal_templates.xml',
    ],
}
