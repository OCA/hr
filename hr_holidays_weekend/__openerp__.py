# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2014 initOS GmbH(<http://www.initos.com>).
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
    "name": "Holidays Weekend",
    "version": '1.0',
    "depends": [
        "hr_holidays",
        "hr_public_holidays",
        "hr_contract",
    ],
    'author': 'initOS GmbH',
    "category": "",
    'license': 'AGPL-3',
    "description": """
    The module uses hr_contract and add functionality for calculation
    of the leave days according to the applied working days as well as
    calculate the public holidays according
    to the country and state
    """,
    "summary": "",
    'data': [
        'hr_holidays_view.xml',
        'security/ir.model.access.csv',
        'security/hr_contract_employee.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
