# -*- coding: utf-8 -*-
# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)
{
    'name': 'Worked Days From Timesheet',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Acysos S.L.,"
    "Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
        'hr_timesheet_sheet',
    ],
    'data': [
        'views/hr_payslip_view.xml'
    ],
    'installable': True,
}
