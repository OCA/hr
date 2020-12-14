# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    expense_invoice_id = fields.Many2one(
        "account.invoice", string="Invoice", readonly=True, copy=False
    )
