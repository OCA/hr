# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
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
#

{
    'name': 'Overtime Policy',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Define Overtime Policies
========================
Define properties of an overtime policy, such as:
    * Type (daily, weekly, or holiday)
    * Rate (multiplier of base wage)
    * Active Hours
    """,
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_policy_group',
    ],
    'data': [
        'security/ir.model.access.csv',
        'hr_policy_ot_view.xml',
    ],
    'test': [
    ],
    'installable': True,
}
