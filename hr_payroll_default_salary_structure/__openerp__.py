# -*- coding: utf-8 -*-
###############################################################################
#
#    Copyright (C) 2016 Salton Massally (<smassally@idtlabs.sl>).
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
    "name": "Default Salary Structure",
    "version": "0.1",
    'author': "Salton Massally <smassally@idtlabs.sl>, "
               "Odoo Community Association (OCA)",
    "website": "http://idtlabs.sl",
    "category": "Human Resources",
    "summary": "Allows you to mark a salary structure that is automatically "
               "selected for new contracts",
    "depends": [
        'hr_payroll'
    ],
    "data": [
        'views/res_config.xml',
    ],
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
