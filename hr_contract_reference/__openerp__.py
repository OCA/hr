# -*- coding:utf-8 -*-
##############################################################################
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
##############################################################################
{
    "name": "HR Contract Reference",
    "version": "8.0.1.0.0",
    "category": "Generic Modules/Human Resources",
    "author": 'Michael Telahun Makonnen, '
              'Fekete Mihai (Forest and Biomass Services Romania), '
              'Odoo Community Association (OCA)',
    "website": "http://miketelahun.wordpress.com",
    "license": "AGPL-3",
    "depends": ["hr_contract"],
    "data": [
        'views/hr_contract_view.xml',
        'data/hr_contract_sequence.xml',
    ],
    'installable': True,
}
