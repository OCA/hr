# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    expense_ids = fields.One2many(
        comodel_name="hr.expense", inverse_name="invoice_id", string="Expenses"
    )

    @api.constrains("amount_total")
    def _check_expense_ids(self):
        for invoice in self.filtered("expense_ids"):
            DecimalPrecision = self.env["decimal.precision"]
            precision = DecimalPrecision.precision_get("Product Price")
            expense_amount = sum(invoice.expense_ids.mapped("total_amount"))
            if float_compare(expense_amount, invoice.amount_total, precision) != 0:
                raise ValidationError(
                    _(
                        "You can't change the total amount, as there's an expense "
                        "linked to this invoice."
                    )
                )
