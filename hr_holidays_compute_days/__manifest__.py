# -*- coding: utf-8 -*-
# ©  2015 iDT LABS (http://www.@idtlabs.sl)
# © 2016 MONK Software (http://www.wearemonk.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Employee Compute Leave Days',
    'version': '10.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Computes the actual leave days '
               'considering rest days and public holidays',
    'author': 'iDT LABS, '
              'MONK Software, '
              'Odoo Community Association (OCA)',
    'website': 'http://idtlabs.sl',
    'depends': ['hr', 'hr_holidays', 'hr_public_holidays'],
    'data': [
        'views/hr_holidays_status.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],
    'installable': True,
}
