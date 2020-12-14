# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    expense_ids = fields.One2many(
        "hr.expense", "expense_invoice_id",
        string="Expenses", readonly=True, copy=False
    )
    expense_count = fields.Integer(
        "Number of expenses", compute="_compute_expense_count"
    )

    @api.multi
    @api.depends("expense_ids")
    def _compute_expense_count(self):
        expense_data = self.env["hr.expense"].read_group(
            [("expense_invoice_id", "in", self.ids)],
            ["expense_invoice_id"],
            ["expense_invoice_id"],
        )
        mapped_data = dict(
            [
                (t["expense_invoice_id"][0], t["expense_invoice_id_count"])
                for t in expense_data
            ]
        )
        for invoice in self:
            invoice.expense_count = mapped_data.get(invoice.id, 0)


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.model
    def create(self, values):
        invoice_line = super(AccountInvoiceLine, self).create(values)
        if (
            invoice_line.invoice_id.type == "out_invoice"
            and invoice_line.invoice_id.state == "draft"
        ):
            sale_line_delivery = invoice_line.sale_line_ids.filtered(
                lambda sol: sol.product_id.invoice_policy == "delivery"
                and sol.product_id.expense_policy == "cost"
                and sol.product_id.type == 'service'
            )
            if sale_line_delivery:
                expenses = self.env['hr.expense'].search(
                    [('sale_order_id', '=', sale_line_delivery.order_id.id),
                     ('expense_invoice_id', '=', False)])
                expenses.write({
                    'expense_invoice_id': invoice_line.invoice_id.id,
                })
        return invoice_line
