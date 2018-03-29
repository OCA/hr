# -*- coding:utf-8 -*-
#
#
#    Copyright (C) 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
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
    'name': 'Department Sequence',
    'version': '10.0.1.0.0',
    'category': 'Generic Modules/Human Resources',
    'summary': """Add sequence on department""",
    'author': "Michael Telahun Makonnen <mmakonnen@gmail.com>,"
              "Odoo Community Association (OCA)",
    'website': 'http://www.openerp.com',
    'license': 'AGPL-3',
    'depends': [
        'hr',
    ],
    'data': [
        'views/hr_department_view.xml',
    ],
    'installable': True,
}
