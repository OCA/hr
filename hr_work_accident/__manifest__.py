# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Hr Work Accident',
    'summary': """
        Module to manage work accidents""",
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'Creu Blanca,Odoo Community Association (OCA)',
    'website': 'www.github.com/OCA/hr',
    'depends': [
        'hr_employee_seniority',
    ],
    'data': [
        'data/ir_sequence_data.xml',
        'reports/hr_work_accident_report.xml',
        'security/ir.model.access.csv',
        'views/hr_work_accident.xml',
    ],
}
