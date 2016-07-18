# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. (
# <http://www.eficent.com>).
# © 2015 Ecosoft Pvt Ltd. (# <http://www.ecosoft.co.th>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class HrExpenseExpense(models.Model):
    
    _inherit = 'hr.expense.expense'

    @api.multi
    @api.depends('account_move_id')
    def _compute_payment_ids(self):
        for expense in self:
            src = []
            lines = []
            if expense.account_move_id:
                for m in expense.account_move_id.line_id:
                    temp_lines = []
                    if m.reconcile_id:
                        temp_lines = map(
                            lambda x1: x, m.reconcile_id.line_id)
                    elif m.reconcile_partial_id:
                        temp_lines = map(
                            lambda x2: x,
                            m.reconcile_partial_id.line_partial_ids)
                    lines += [x for x in temp_lines if x not in lines]
                    src.append(m)

            lines = filter(lambda x3: x not in src, lines)
            expense.payment_ids = lines

    payment_ids = fields.Many2many(compute=_compute_payment_ids,
                                   comodel_name='account.move.line',
                                   string='Payments')

    @api.multi
    def expense_canceled(self):
        account_move_obj = self.env['account.move']
        moves = account_move_obj.browse([])
        for expense in self:
            if expense.account_move_id:
                moves += expense.account_move_id
            if expense.payment_ids:
                for move_line in expense.payment_ids:
                    if move_line.reconcile_partial_id and \
                            move_line.reconcile_partial_id.line_partial_ids:
                        raise UserError(_('You cannot cancel an expense '
                                          'which is partially paid. '
                                          'You need to unreconcile related '
                                          'payment entries first.'))

            expense.move_id = False
        if moves:
            moves.button_cancel()
            moves.unlink()

        # Call super method.
        res = super(HrExpenseExpense, self).expense_canceled()
        return res
