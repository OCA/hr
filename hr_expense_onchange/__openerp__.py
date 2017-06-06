# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Onchange module for OpenERP
#    Copyright (C) 2014 Akretion (http://www.akretion.com)
#    @author Alexis de Lattre <alexis.delattre@akretion.com>
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
    'name': 'Onchange on Expenses',
    'version': '0.1',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': "Adds on_change on some fields of expense lines",
    'description': """
Onchange on Expenses
====================

This is a technical module that adds *on_change* on 2 fields of expense
lines : *unit_amount* and *unit_quantity*. This module is not designed
to be used alone ; it is designed to be used as a technical base for
other modules that depend on this one.

This module has been written by Alexis de Lattre
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['hr_expense'],
    'data': ['hr_expense_view.xml'],
    'installable': True,
}
