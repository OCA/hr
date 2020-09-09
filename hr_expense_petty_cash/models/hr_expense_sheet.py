# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def _default_journal_id(self):
        """ Update expense journal from petty cash """
        journal = super()._default_journal_id()
        petty_cash_obj = self.env['petty.cash']
        petty_cash = self._context.get('default_petty_cash_id', False)
        if petty_cash:
            petty_cash_id = petty_cash_obj.browse(petty_cash)
            journal = petty_cash_id.journal_id.id or journal
        return journal

    payment_mode = fields.Selection(
        selection_add=[('petty_cash', 'Petty Cash')],
    )
    petty_cash_id = fields.Many2one(
        string='Petty cash holder',
        comodel_name='petty.cash',
        ondelete='restrict',
        readonly=True,
        compute='_compute_petty_cash',
    )
    journal_id = fields.Many2one(
        default=_default_journal_id
    )

    @api.depends('expense_line_ids', 'payment_mode')
    def _compute_petty_cash(self):
        for rec in self:
            if rec.payment_mode == 'petty_cash':
                set_petty_cash_ids = set()
                for line in rec.expense_line_ids:
                    set_petty_cash_ids.add(line.petty_cash_id.id)
                if len(set_petty_cash_ids) == 1:
                    rec.petty_cash_id = rec.env['petty.cash'].browse(
                        set_petty_cash_ids.pop())
                else:
                    raise ValidationError(_('You cannot create report from '
                                            'many petty cash holders.'))

    @api.multi
    @api.constrains('expense_line_ids', 'total_amount')
    def _check_petty_cash_amount(self):
        for rec in self:
            if rec.payment_mode == 'petty_cash':
                petty_cash = rec.petty_cash_id
                balance = petty_cash.petty_cash_balance
                amount = rec.total_amount
                company_currency = rec.company_id.currency_id
                amount_company = rec.currency_id._convert(
                    amount, company_currency, rec.company_id,
                    rec.accounting_date or fields.Date.today())
                prec = rec.currency_id.rounding
                if float_compare(
                        amount_company, balance, precision_rounding=prec) == 1:
                    raise ValidationError(
                        _('Not enough money in petty cash holder.\n'
                          'You are requesting %s%s, '
                          'but the balance is %s%s.') %
                         ('{:,.2f}'.format(amount_company),
                          company_currency.symbol, '{:,.2f}'.format(balance),
                          company_currency.symbol))
