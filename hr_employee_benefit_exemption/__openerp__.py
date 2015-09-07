# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015 Savoir-faire Linux. All Rights Reserved.
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
    'name': 'Employee Benefit Exemption',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'author': "Savoir-faire Linux, Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com',
    'description': """
Employee Benefit Exemption
==========================
Add exemptions on employee benefit categories.
    """,
    'depends': [
        'hr_employee_benefit',
        'hr_employee_exemption',
    ],
    'data': [
        'views/hr_employee_benefit_category.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
