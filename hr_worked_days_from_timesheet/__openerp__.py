# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Odoo Canada. All Rights Reserved.
#    Copyright (C) 2015 Acysos S.L. All Rights Reserved.
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
    'name': 'Worked Days From Timesheet',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Acysos SL, \
    Acysos S.L., \
    Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_payroll',
        'hr_timesheet_sheet',
    ],
    'data': [
        'views/hr_payslip_view.xml'
    ],
    'test': [
        'test/worked_days_from_timesheet_test.yml'
    ],
    'installable': True,
}
