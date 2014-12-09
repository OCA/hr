# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
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
=====================
The aim of this module is to allow users to enter details on their timesheet.

With this module, employees can select an Activity which can be a leave type
or a specific job position.

This will allow in another module to import the hours from timesheet
to worked days and distinguish every hour passed for each activity.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_timesheet_sheet',
        'hr_worked_days_activity',
        'hr_contract_multi_jobs',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_contract_security.xml',
        'hr_analytic_timesheet_view.xml',
        'hr_timesheet_sheet_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
    'js': ['static/src/js/timesheet.js'],
    'css': ['static/src/css/timesheet.css'],
    'qweb': ['static/src/xml/timesheet.xml'],
}
