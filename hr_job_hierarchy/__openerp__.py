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
    'name': 'Job Hierarchy',
    'version': '1.0',
    'category': 'Generic Modules/Human Resources',
    'description': """
Define Hierarchy of Jobs
========================

    1. Define parent/child relationship for jobs, which is useful for
       determining supervisor/subordinate relationships.
    2. Provide a knob in Job configuration to specify if the person with that
       job should be considered the Department manager.
    3. Automatically set the manager of a department based on this knob in job
       configuration.
    4. Automatically set an employee's manager from the department's manager.
    """,
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,Odoo Community Association (OCA)",
    'website': 'http://miketelahun.wordpress.com',
    'depends': [
        'hr_contract',
    ],
    'data': [
        'hr_view.xml',
    ],
    'test': [
    ],
    'installable': True,
}
