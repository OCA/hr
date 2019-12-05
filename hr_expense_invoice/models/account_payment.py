# Copyright 2019 Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import ValidationError


class AccountPayment(models.Model):
    _inherit = "account.payment"

    def action_validate_invoice_payment(self):
        # Do not allow register payment for invoices from expenses
        expenses = (
            self.env["hr.expense"]
            .sudo()
            .search([("invoice_id", "in", self.invoice_ids.ids)])
        )
        if expenses:
            raise ValidationError(
                _("Register payment on expense's " "invoice is not allowed")
            )
        return super(AccountPayment, self).action_validate_invoice_payment()
