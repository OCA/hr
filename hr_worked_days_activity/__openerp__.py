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
    'name': 'Worked Days Activity',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Worked Days Activity
====================
This module adds the activity field on payslip worked days. It is used to
distinguish the leaves types and job positions in worked days.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'data/hr_holiday_status_data.xml',
        'data/hr_activity_data.xml',
        'view/hr_holiday_status_view.xml',
        'view/hr_payslip_view.xml',
        'view/hr_activity_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': ['test/hr_activity_test.yml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
