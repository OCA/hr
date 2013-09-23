#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
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
    'name': 'Simplify Employee Records.',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Make Employee Records and Contracts Easier to Work With
=======================================================
    1. Make the job id in employee object reference job id in latest contract.
    2. When moving from employee to contract pre-populate the employee field.
    3. In the contract form show only those positions belonging to the
       department the employee belongs to.
    4. Make country (nationality) default to Ethiopia
    5. Make official identification document number unique
    """,
    'author': 'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
        'hr_contract',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'hr_simplify_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
