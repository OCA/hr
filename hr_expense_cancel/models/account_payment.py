# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    expense_sheet_id = fields.Many2one(
        comodel_name="hr.expense.sheet", string="Expense sheet"
    )
