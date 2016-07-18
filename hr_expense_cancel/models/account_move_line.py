# -*- coding: utf-8 -*-
# © 2016 Eficent Business and IT Consulting Services S.L. (
# <http://www.eficent.com>).
# © 2015 Ecosoft Pvt Ltd. (# <http://www.ecosoft.co.th>).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models, _
from openerp.exceptions import Warning as UserError


class AccountMoveLine(models.Model):
    
    _inherit = 'account.move.line'

    @api.model
    def _remove_move_reconcile(self,
                               move_ids=None, opening_reconciliation=False):
        res = super(AccountMoveLine, self)._remove_move_reconcile(
            move_ids=move_ids, opening_reconciliation=opening_reconciliation)
        for line in self.browse(move_ids):
            expense = self.env['hr.expense.expense'].search(
                [('account_move_id', '=', line.move_id.id)])
            if expense and expense.state == 'paid':
                expense.write({'state': 'done'})
        return res
