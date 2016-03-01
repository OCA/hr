# -*- coding: utf-8 -*-

###############################################################################
#
#    Copyright (C) 2015 Daniel Reis
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
###############################################################################

{
    'name': 'Applicants implicit Partner',
    'summary': 'Automatically create a Partner for Applicants',
    'version': '8.0.1.0.0',
    'category': 'Human Resources',
    'author': 'Daniel Reis, Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'data': [
        'views/hr_applicant_view.xml',
    ],
    'depends': [
        'hr_recruitment',
    ],
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'installable': True,
}
