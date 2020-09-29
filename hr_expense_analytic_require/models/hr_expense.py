# Copyright (C) 2020 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    analytic_account_id = fields.Many2one(
        required=True,
        default=lambda self:
        self.env.user.company_id.default_expense_analytic_id)
