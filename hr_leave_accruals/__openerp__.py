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
    'name': 'Leave Accruals',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Leave Accruals
==============
This module adds leave accruals on employees and a mechanism to compute these
automaticaly.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': 'Savoir-faire Linux',
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
    ],
    'data': [
        'security/ir.model.access.csv',
        'view/hr_employee_view.xml',
        'view/hr_leave_accrual_view.xml',
        'view/hr_holidays_status_view.xml',
        'view/res_company_view.xml',
    ],
    'test': ['test/hr_leave_accruals_test.yml'],
    'demo': [],
    'installable': True,
}
