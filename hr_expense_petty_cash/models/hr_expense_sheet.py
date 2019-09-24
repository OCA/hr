# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    payment_mode = fields.Selection(
        selection_add=[('petty_cash', 'Petty Cash')],
    )
    petty_cash_id = fields.Many2one(
        string='Petty cash holder',
        comodel_name='petty.cash',
        ondelete='restrict',
        readonly=True,
    )

    @api.multi
    @api.constrains('expense_line_ids')
    def _check_petty_cash_amount(self):
        for rec in self:
            petty_cash = self.env['petty.cash'].search(
                [('id', '=', self.petty_cash_id.id)], limit=1)
            balance = petty_cash.petty_cash_balance
            amount = self.total_amount
            company_currency = rec.company_id.currency_id
            amount_company = rec.currency_id.compute(amount, company_currency)
            if amount_company > balance:
                raise ValidationError(
                    _('Not enough money in petty cash holder.\n'
                      'You are requesting %s %s, but the balance is %s %s.') %
                    ('{:,.2f}'.format(amount_company), company_currency.symbol,
                     '{:,.2f}'.format(balance), company_currency.symbol))
