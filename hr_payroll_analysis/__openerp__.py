# -*- coding:utf-8 -*-
{
    'name': 'Payroll Analysis',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'summary': "Adds a report over amounts of payslips line related to a "
               "a salary rule.",
    'author': "Savoir-faire Linux, "
              "Salton Massally (iDT Labs) "
              "Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'wizard/payroll_analysis_view.xml',
        'views/hr_salary_rule_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
