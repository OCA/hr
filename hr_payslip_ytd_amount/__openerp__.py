# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 - 2015 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Payslip Year-to-date Amount',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Payslip Year-to-date Amount
===========================
This module adds a field in payslip lines for year-to-date amounts.

The year-to-date value is calculated only for the rules that appear on payslip
after the computation of the payslip.

The purpose of this module is to eliminate redondant rules that calculate
the year-to-date value of other rules.

The module provides a payslip report with 3 columns:
 - The salary rule name
 - The amount for the actual payslip
 - The amount year-to-date

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'hr_payslip_view.xml',
        'report/hr_payslip_ytd_amount_report.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
