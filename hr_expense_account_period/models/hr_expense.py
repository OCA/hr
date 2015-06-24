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

from openerp import models, api, fields


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    period_id = fields.Many2one('account.period', string='Force Period',
                                copy=False)

    @api.model
    def account_move_get(self, expense_id):
        res = super(HrExpenseExpense, self).account_move_get(expense_id)
        expense = self.browse([expense_id])[0]
        if expense.period_id.id:
            res['period_id'] = expense.period_id.id
        return res
