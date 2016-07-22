# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Aaron Henriquez (Eficent)
#    Copyright 2016 Eficent
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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
    'name': 'Change the state of payslip in tree view',
    'version': '1.0',
    'category': 'Human Resources',
    'description': '''
Change the state of selected payslips in list view
''',
    'author': "Eficent",
    'website': 'http://www.eficent.com',
    'depends': ['hr_payroll_cancel'],
    "demo": [],
    "data": [
        "wizard/hr_payslip_change_state_view.xml",
    ],
    "test": [],
    "js": [],
    "css": [],
    "qweb": [],
    "installable": True,
    "auto_install": False,
    "active": False
}
