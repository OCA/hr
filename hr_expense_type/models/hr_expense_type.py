# Copyright (C) 2022 Trey, Kilobytes de Soluciones - Vicent Cubells
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrExpenseType(models.Model):
    _name = "hr.expense.type"
    _description = "Define Expense Types"

    name = fields.Char(
        string="Name",
        required=True
    )
    code = fields.Char()
    description = fields.Text()
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.user.company_id,
        required=True,
    )
