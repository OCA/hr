# -*- coding: utf-8 -*-
# © 2014 Savoir-faire Linux (https://www.savoirfairelinux.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


{
    'name': 'Payslip Year-to-date Amount',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Payslip Year-to-date Amount
===========================
This module adds a field in payslip lines for year-to-date amounts.
 * The purpose of this module is to eliminate redondant rules that calculate the year-to-date value of other rules.  
 * The year-to-date value is calculated only for the rules that appear on payslip
 * The calculation is done just after payslip computation.
The purpose of this module is to eliminate redondant rules that calculate
the year-to-date value of other rules.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
* Bassirou Ndaw <b.ndaw@ergobit.org>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA),Ergobit Consulting",
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'views/hr_payslip_view.xml'
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
