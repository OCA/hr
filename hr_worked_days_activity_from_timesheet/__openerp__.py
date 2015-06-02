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
    'name': 'Worked Days Activities From Timesheet',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'AGPL-3',
    'description': """
Worked Days Activities From Timesheet
=====================================
Import worked days from the timesheet with activities and hourly rates.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_contract_hourly_rate',
        'hr_activity_on_timesheet',
        'hr_worked_days_hourly_rate',
        'hr_worked_days_activity',
        'hr_worked_days_from_timesheet',
    ],
    'data': [],
    'test': [],
    'demo': [],
    'installable': True,
}
