# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of hr_expense_account_period,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     hr_expense_account_period is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     hr_expense_account_period is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with hr_expense_account_period.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "HR Expense Account Period",

    'summary': """Accounting period for HR expenses journal entries""",
    'author': "ACSONE SA/NV,Odoo Community Association (OCA)",
    'website': "http://acsone.eu",
    'category': 'Human Resources',
    'version': '8.0.0.1.0',
    'license': 'AGPL-3',
    'depends': [
        'hr_expense',
    ],
    'data': [
        'view/hr_expense_view.xml',
    ],
}
