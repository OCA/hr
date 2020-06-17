# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    'name': 'Talent Management',
    'version': '12.0.1.0.0',
    'category': 'Human Resources',
    'website': 'https://github.com/OCA/hr',
    'author':
        'Brainbean Apps, '
        'Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'summary': 'Source, research, and keep track of talents for future jobs',
    'depends': [
        'hr_recruitment',
        'hr_skill',
        'queue_job',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_talent.xml',
        # 'views/project_assignment.xml',
        # 'views/project_project.xml',
        # 'views/project_role.xml',
        # 'views/res_config_settings.xml',
        'wizards/hr_talent_sourcing_wizard.xml',
    ],
    'maintainers': [
        'alexey-pelykh',
    ],
}
