# -*- encoding: utf-8 -*-
##############################################################################
#
#    HR Expense Analytic Default module for OpenERP
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
    'name': 'Default Analytic on Expenses',
    'version': '8.0.0.1.0',
    'category': 'Human Resources',
    'license': 'AGPL-3',
    'summary': "Manage default analytic account on expenses",
    'description': """
Default Analytic on Expenses
===========================

This module adds 2 fields:

* *Default Analytic Account* on the employee form (*HR Settings* tab),

* *Default Analytic Account* on the expense form.

If you set a Default Analytic Account on the employee, it will be copied
to the Default Analytic Account of the expenses of this employee. The
Default Analytic Account of the expense is used by default on each
expense line.

This module has been written by Alexis de Lattre
<alexis.delattre@akretion.com>.
    """,
    'author': 'Akretion',
    'website': 'http://www.akretion.com',
    'depends': ['hr_expense'],
    'data': [
        'hr_employee_view.xml',
        'hr_expense_view.xml',
    ],
    'demo': ['expense_analytic_default_demo.xml'],
    'installable': True,
}
