# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    petty_cash_id = fields.Many2one(
        string="Petty cash holder",
        comodel_name="petty.cash",
        related="expense_line_ids.petty_cash_id",
        ondelete="restrict",
        readonly=True,
    )

    def action_submit_sheet(self):
        self._check_petty_cash_amount()
        return super().action_submit_sheet()

    def _check_petty_cash_amount(self):
        if self.payment_mode == "petty_cash":
            petty_cash = self.petty_cash_id
            balance = petty_cash.petty_cash_balance
            amount = self.total_amount
            company_currency = self.company_id.currency_id
            amount_company = self.currency_id.compute(amount, company_currency)
            if amount_company > balance:
                raise ValidationError(
                    _(
                        "Not enough money in petty cash holder.\n"
                        "You are requesting %s%s, but the balance is %s%s."
                    )
                    % (
                        "{:,.2f}".format(amount_company),
                        company_currency.symbol,
                        "{:,.2f}".format(balance),
                        company_currency.symbol,
                    )
                )
