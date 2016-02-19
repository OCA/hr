# coding: utf-8

from openerp import api, models


class HrExpenseExpense(models.Model):
    _inherit = "hr.expense.expense"

    @api.multi
    def expense_canceled(self):
        account_move_line_obj = self.env['account.move.line']
        res = super(HrExpenseExpense,
                    self).expense_canceled()
        for expense in self:
            if expense.account_move_id:
                all_move_line_ids = [x.id for x in
                                     expense.account_move_id.line_id]
                account_move_line_obj._remove_move_reconcile(all_move_line_ids)
                expense.account_move_id.unlink()
        return res
