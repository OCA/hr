# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    payment_mode = fields.Selection(
        selection_add=[('petty_cash', 'Petty Cash')],
    )
    petty_cash_id = fields.Many2one(
        string='Petty cash holder',
        comodel_name='petty.cash',
        ondelete='restrict',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    def action_submit_expenses(self):
        res = super().action_submit_expenses()
        context = res['context']
        context['default_expense_line_ids'] = self.ids
        context['default_name'] = self[0].name if len(self) == 1 else ''
        set_petty_cash_ids = set()
        for rec in self:
            set_petty_cash_ids.add(rec.petty_cash_id.id)
        if set_petty_cash_ids:
            if len(set_petty_cash_ids) == 1:
                context['default_petty_cash_id'] = set_petty_cash_ids.pop()
                return res
            raise ValidationError(_('You cannot create report from '
                                    'many petty cash holders.'))

    @api.multi
    def _get_account_move_line_values(self):
        res = super()._get_account_move_line_values()
        for expense in self.filtered(
                lambda p: p.payment_mode == 'petty_cash'):
            line = res[expense.id][1]
            line['account_id'] = expense.petty_cash_id.account_id.id
            line['partner_id'] = expense.petty_cash_id.partner_id.id
            res[expense.id][1] = line
        return res
