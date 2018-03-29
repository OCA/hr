# coding: utf-8

from openerp import api, models


class HrExpenseExpense(models.Model):
    _inherit = "hr.expense.expense"

    @api.multi
    def expense_canceled(self):
        res = super(HrExpenseExpense, self).expense_canceled()
        for expense in self:
            if expense.account_move_id:
                expense.account_move_id.button_cancel()
                expense.account_move_id.unlink()
        return res
