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
    'name': 'Contract Hourly Rate',
    'category': 'Localization',
    'version': '1.0',
    'license': 'AGPL-3',
    'category': 'Generic Modules/Human Resources',
    'description': """
Contract Hourly Rate
====================
The objective of this module is to manage employee hourly rates. Annual wage
is still possible. On the contract, the field salary_computation_method allows
to choose between hourly rate and annual wage.

Each contract job belongs to an hourly rate class if the employee is paid
by hourly rates. This allows to manage hourly rate increments over the years
for multiple employees at the same time.

Contributors
------------
* David Dufresne <david.dufresne@savoirfairelinux.com>
* Pierre Lamarche <pierre.lamarche@savoirfairelinux.com>
""",
    'author': "Savoir-faire Linux,Odoo Community Association (OCA)",
    'website': 'https://www.savoirfairelinux.com/',
    'depends': [
        'hr_contract_multi_jobs',
    ],
    'data': [
        'security/ir.model.access.csv',
        'hr_contract_view.xml',
        'hr_hourly_rate_class_view.xml',
    ],
    'test': [],
    'demo': [],
    'installable': True,
}
