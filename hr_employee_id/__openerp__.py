# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2011,2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
    'name': 'Employee ID',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Employee Identification Numbers
===============================
Company wide unique employee ID
    """,
    'author': 'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
    ],
    'data': [
        'hr_view.xml',
    ],
    'test': [
    ],
    'installable': True,
}
