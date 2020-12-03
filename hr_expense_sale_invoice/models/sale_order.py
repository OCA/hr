# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"
    expense_id = fields.Many2one(
        "hr.expense", string="Expense", readonly=True, copy=False
    )
