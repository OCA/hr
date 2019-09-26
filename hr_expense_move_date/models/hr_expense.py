# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api, fields


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    move_date = fields.Date(
        string='Move Date',
    )

    @api.model
    def account_move_get(self, expense_id):
        res = super(HrExpenseExpense, self).account_move_get(expense_id)
        expense = self.browse(expense_id)
        if expense.move_date:
            res['date'] = expense.move_date
        return res

    @api.onchange('move_date')
    def onchange_move_date(self):
        period_obj = self.env['account.period']
        if self.move_date:
            period_ids = period_obj.find(dt=self.move_date)
            if period_ids:
                self.period_id = period_ids[0]
