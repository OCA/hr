# Copyright 2014 Serv. Tecnol. Avanzados (http://www.serviciosbaeza.com)
#                       Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    _rec_name = "number"

    number = fields.Char(required=True, default="/", readonly=True, copy=False)

    @api.model
    def create(self, vals):
        if vals.get("number", "/") == "/":
            number = self.env["ir.sequence"].next_by_code("hr.expense.sheet")
            vals["number"] = number
        return super(HrExpenseSheet, self).create(vals)
