# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    expense_ids = fields.One2many(
        "hr.expense", "expense_invoice_id", string="Expenses", readonly=True, copy=False
    )
    expense_count = fields.Integer(
        "Number of expenses", compute="_compute_expense_count"
    )

    @api.depends("expense_ids")
    def _compute_expense_count(self):
        for invoice in self:
            invoice.expense_count = len(invoice.expense_ids)


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.model_create_multi
    def create(self, vals_list):
        invoice_line = super(AccountMoveLine, self).create(vals_list)
        if (
            invoice_line.move_id.move_type == "out_invoice"
            and invoice_line.move_id.state == "draft"
        ):
            sale_line_delivery = invoice_line.sale_line_ids.filtered(
                lambda sol: sol.product_id.invoice_policy == "delivery"
                and sol.product_id.expense_policy == "cost"
                and sol.product_id.type == "service"
            )
            if sale_line_delivery:
                expenses = self.env["hr.expense"].search(
                    [
                        ("sale_order_id", "=", sale_line_delivery.order_id.id),
                        ("expense_invoice_id", "=", False),
                    ]
                )
                expenses.write(
                    {
                        "expense_invoice_id": invoice_line.move_id.id,
                    }
                )
        return invoice_line
