#-*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Salton Massally <salton.massally@gmail.com>.
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
##############################################################################

{
    'name': 'Employment Termination',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': "Adds the ability to terminate employees",
    'author':'Salton Massally <salton.massally@gmail.com>',
    'website':'http://idtlabs.sl',
    'depends': [
        'hr',
        'hr_contract'
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizard/end_employment_view.xml',
        'data/hr_employee_data.xml',
        'data/cron.xml',
        'views/hr_employee.xml',
        'views/hr_employee_termination.xml',
        'views/hr_employee_termination_reason.xml',
    ],
}
