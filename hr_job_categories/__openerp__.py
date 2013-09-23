#-*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>.
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
    'name': 'Job Categories',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Attach Categories (Tags) to Employees Based on Job Position
===========================================================

This module is useful for tagging employees based on their job positions. For example,
all Supervisors could be attached to the Supervisors category. Define which categries
a job belongs to in the configuration for the job. When an employee is assigned a particular
job the categories attached to that job will be attached to the employee record as well.
    """,
    'author': 'Michael Telahun Makonnen <mmakonnen@gmail.com>',
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'hr_view.xml',
    ],
    'test': [
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}
