# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    reference = fields.Char("Vendor")
    expense_invoice_id = fields.Many2one(
        "account.invoice", string="Invoice", readonly=True, copy=False
    )

    @api.onchange("analytic_account_id")
    def _onchange_analytic_account_id(self):
        for rec in self:
            if rec.analytic_account_id:
                rec.sale_order_id = self.env["sale.order"].search(
                    [("analytic_account_id", "=", rec.analytic_account_id.id)],
                    limit=1,
                    order="id desc",
                )
