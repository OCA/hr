# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Show Taxes module for OpenERP
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
    'name': 'Show Taxes on Expenses',
    'version': '0.1',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': "Show tax amount on expense lines and total taxes on expenses",
    'description': """
Show Taxes on Expenses
======================

With this modules, you will see the untaxed amount and tax amount on
each expense line. You will also see the total untaxed and total taxes
of the expense.

This module has 2 other features related to taxes on expenses:

* it adds a constraint on *Can be Expensed* products to check that the
Supplier Taxes are *Tax Included*,

* it disable the use of the Default Taxes of the Expense Account of the
product : by default, if the product doesn't have any Supplier Taxes but
the Expense Account has Default Taxes, OpenERP will uses these Default
Taxes ; the module disables the use of these Default Taxes because
it will probably lead the company to get back VAT where it shouldn't
without being conscious of it.

This module has been written by Alexis de Lattre
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['hr_expense_onchange'],
    'data': ['hr_expense_view.xml'],
    'installable': True,
}
