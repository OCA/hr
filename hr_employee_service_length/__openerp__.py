# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2015 Salton Massally (<smassally@idtlabs.sl>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Employee Service Length',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Human Resources',
    'summary': "Calculates the length of an employee's time in a company",
    'author': "Salton Massally <smassally@idtlabs.sl>, "
              "Odoo Community Association (OCA)",
    'website': 'http://idtlabs.sl',
    'license': 'AGPL-3',
    'depends': ['hr_contract'],
    "external_dependencies": {
        'python': ['dateutil'],
    },
    'data': [
        'views/hr_employee.xml',
    ],
    'installable': True,
}
