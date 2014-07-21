# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2014 initOS GmbH & Co. KG (<http://www.initos.com>).
#    Author Andy Kanner <andy.kenner@initos.com>
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
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
    "name": "Hr holidays weekend module",
    "version": '0.1',
    "depends": [
                "hr_holidays",
                "hr_public_holidays"
                ],
    'author': 'initOS GmbH & Co. KG',
    "category": "",
    'license': 'AGPL-3',
    "description": """
    Excludes weekend days from calculation of holidays

    The module extend hr_employee by adding option for configure
    the count of working days (5 or 6).
    The module extends hr_holidays by adding functionality for calculation
    of the leave days according to the applied working days as well as
    calculate the public holidays according
    to the country and state
    """,
    "summary": "",
    'data': [
             'hr_holidays_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
