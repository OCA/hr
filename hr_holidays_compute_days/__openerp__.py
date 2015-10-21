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
    'name': 'Employee Compute Leave Days',
    'version': '8.0.1.0.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': 'Computes the actual days for which employee will be on leave '
               'taking into account both rest days and public holidays',
    'author': 'Salton Massally<smassally@idtlabs.sl>',
    'website': 'http://idtlabs.sl',
    'depends': ['hr_holidays', 'hr_public_holidays'],
    'data': [
        'views/hr_holidays_status.xml',
    ],
    'installable': True,
}
