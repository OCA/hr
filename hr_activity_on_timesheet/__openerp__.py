# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2012 - 2014 Odoo Canada. All Rights Reserved.
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
    'name': 'Activity on Timesheet',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Activity on Timesheet
====================
The aim of this module is to allow user to enter details on their timesheet to
prepare correctly the payslip.

With this module, employee can select an analytic account on his timesheet line
and an Activity which can be leave type or specific job position.

This module is good to detail the exact activity of employees in order to have
the relevant information to prepare the payroll for a period.

What it does :

- Create a new object "Activity" which is a list of leave types and job
    position
- Create a tab on analytic account form to select autorized activities on this
    specific analytic account
- Create a column on timesheet to define one of the autorized Activity of the
    selected analytic account

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_timesheet',
        'hr_timesheet_sheet',
        'hr_timesheet_invoice',
        'hr_worked_days_from_timesheet',
        'analytic'
    ],
    'data': [
        'account_analytic_account_view.xml',
        'hr_analytic_timesheet_view.xml',
        'hr_analytic_timesheet_activity_view.xml',
        'hr_payslip_view.xml',
        'hr_timesheet_sheet_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'js': ['static/src/js/timesheet.js', ],
    'css': ['static/src/css/timesheet.css', ],
    'qweb': ['static/src/xml/timesheet.xml', ],
}
