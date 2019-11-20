# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    is_petty_cash = fields.Boolean(
        string="Petty Cash", readonly=True, states={"draft": [("readonly", False)]}
    )

    def action_post(self):
        self._check_petty_cash_amount()
        return super().action_post()

    def _check_petty_cash_amount(self):
        petty_cash_env = self.env["petty.cash"]
        for rec in self.filtered("is_petty_cash"):
            petty_cash = petty_cash_env.search(
                [("partner_id", "=", rec.partner_id.id)], limit=1
            )
            if not petty_cash:
                raise ValidationError(
                    _("%s is not a petty cash holder") % rec.partner_id.name
                )
            balance = petty_cash.petty_cash_balance
            limit = petty_cash.petty_cash_limit
            max_amount = limit - balance
            account = petty_cash.account_id
            amount = sum(
                rec.invoice_line_ids.filtered(lambda l: l.account_id == account).mapped(
                    "price_subtotal"
                )
            )
            company_currency = rec.company_id.currency_id
            amount_company = rec.currency_id.compute(amount, company_currency)
            if amount_company > max_amount:
                raise ValidationError(
                    _("Petty Cash balance is %s %s.\n" "Max amount to add is %s %s.")
                    % (
                        "{:,.2f}".format(balance),
                        company_currency.symbol,
                        "{:,.2f}".format(max_amount),
                        company_currency.symbol,
                    )
                )

    def _add_petty_cash_invoice_line(self, petty_cash):
        self.ensure_one()
        # Get suggested currency amount
        amount = petty_cash.petty_cash_limit - petty_cash.petty_cash_balance
        company_currency = self.env.user.company_id.currency_id
        amount_doc_currency = company_currency.compute(amount, self.currency_id)

        move_line = self.env["account.move.line"].new(
            {
                "name": petty_cash.account_id.name,
                "account_id": petty_cash.account_id.id,
                "price_unit": amount_doc_currency,
                "quantity": 1,
            }
        )
        return move_line

    @api.onchange("is_petty_cash", "partner_id")
    def _onchange_is_petty_cash(self):
        self.invoice_line_ids = False
        if self.is_petty_cash:
            if not self.partner_id:
                raise ValidationError(_("Please select petty cash holder"))
            # Selected parenter must be petty cash holder
            petty_cash = self.env["petty.cash"].search(
                [("partner_id", "=", self.partner_id.id)], limit=1
            )
            if not petty_cash:
                raise ValidationError(
                    _("%s is not a petty cash holder") % self.partner_id.name
                )
            self.invoice_line_ids = self._add_petty_cash_invoice_line(petty_cash)
