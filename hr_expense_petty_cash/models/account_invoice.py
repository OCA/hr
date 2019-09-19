# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    is_petty_cash = fields.Boolean(
        string='Petty Cash',
        default=False,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    @api.multi
    @api.constrains('invoice_line_ids')
    def _check_petty_cash_amount(self):
        for rec in self:
            if not rec.is_petty_cash:
                continue
            petty_cash = self.env['petty.cash'].search(
                [('partner_id', '=', self.partner_id.id)], limit=1)
            if not petty_cash:
                raise ValidationError(_('%s is not a petty cash holder') %
                                      self.partner_id.name)
            balance = petty_cash.petty_cash_balance
            limit = petty_cash.petty_cash_limit
            max_amount = limit - balance
            account = petty_cash.account_id
            # Looking for petty cash line
            inv_lines = rec.invoice_line_ids.filtered(
                lambda l: l.account_id == account)
            amount = sum([line.price_subtotal for line in inv_lines])
            company_currency = rec.company_id.currency_id
            amount_company = rec.currency_id.compute(amount, company_currency)
            if amount_company > max_amount:
                raise ValidationError(
                    _('Petty Cash balance is %s %s.\n'
                      'Max amount to add is %s %s.') %
                    ('{:,.2f}'.format(balance), company_currency.symbol,
                     '{:,.2f}'.format(max_amount), company_currency.symbol))

    @api.model
    def _add_petty_cash_invoice_line(self, petty_cash):
        # Get suggested currency amount
        amount = petty_cash.petty_cash_limit - petty_cash.petty_cash_balance
        company_currency = self.env.user.company_id.currency_id
        amount_doc_currency = \
            company_currency.compute(amount, self.currency_id)

        inv_line = self.env['account.invoice.line'].new({
            'name': petty_cash.account_id.name,
            'invoice_id': self.id,
            'account_id': petty_cash.account_id.id,
            'price_unit': amount_doc_currency,
            'quantity': 1,
        })
        return inv_line

    @api.multi
    @api.onchange('is_petty_cash', 'partner_id')
    def _onchange_is_petty_cash(self):
        self.invoice_line_ids = False
        if self.is_petty_cash:
            if not self.partner_id:
                self.is_petty_cash = False
                raise ValidationError(_('Please select petty cash holder'))
            # Selected parenter must be petty cash holder
            petty_cash = self.env['petty.cash'].search(
                [('partner_id', '=', self.partner_id.id)], limit=1)
            if not petty_cash:
                self.is_pettycash = False
                raise ValidationError(_('%s is not a petty cash holder') %
                                      self.partner_id.name)
            self._add_petty_cash_invoice_line(petty_cash)
