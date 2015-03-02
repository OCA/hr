# -*- coding: utf-8 -*-
#
#
#    Daniel Reis
#    2012
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
#


{
    'name': 'HR Groups and Security Extensions',
    'version': '6.1',
    'category': 'Human Resources',
    'description': """Additional roles and security enhancementes, as a base for more complex HR processes.
 At HR Management level, there two roles provided bu standard: HR Manager and HR Office.
 At the rest of the organization, three roles are available:
 * Employee: each individual. Has only has read access to own employee data.
 * Manager Assistant: has read and write access to all employees.
 * Employee Manager: has read and write access to all employees.

 """,
    'author': "Daniel Reis,Odoo Community Association (OCA)",
    'website': 'daniel.reis@securitas.pt',
    'depends': [
        'hr',
    ],
    'init_xml': [],
    'update_xml': [
        'hr_view.xml',
        'security/hr_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo_xml': [],
    'test': [],
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
