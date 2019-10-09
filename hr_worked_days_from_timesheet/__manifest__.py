# -*- coding: utf-8 -*-
# © 2012 Odoo Canada
# © 2015 Acysos S.L.
# © 2017 Eficent Business and IT Consulting Services S.L.
# Copyright 2017 Serpent Consulting Services Pvt. Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    'name': 'HR Worked Days From Timesheet',
    'summary': 'Adds a button to import worked days from timesheet.',
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Acysos S.L., Eficent, "
              "Serpent Consulting Services Pvt. Ltd.,"
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
