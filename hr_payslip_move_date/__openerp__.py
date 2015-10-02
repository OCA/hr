# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Eficent (<http://www.eficent.com/>)
#              Jordi Ballester Alomar <jordi.ballester@eficent.com>
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
    "name": "HR Payslip Move Date",
    "version": "1.0",
    "license": 'AGPL-3',
    "author": "Eficent, Odoo Community Association (OCA)",
    "category": "Generic Modules/Human Resources",
    "depends": ["hr_payroll_account"],
    "description": """
HR Payslip Move Date
====================
Adds a move date to the payslip.
Allows the user to propose/force a specific move date.
If none is proposed, the field will be completed with the actual move date.
    """,
    "data": [
        "views/hr_payslip_view.xml"
    ],
    'demo': [],
    'test':[
    ],
    'installable': True,
}
