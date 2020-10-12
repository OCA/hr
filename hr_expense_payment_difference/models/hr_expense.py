# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields


class HRExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    residual = fields.Monetary(
        compute='_compute_residual',
    )

    def _compute_residual(self):
        for sheet in self:
            types = ('payable', 'receivable')
            lines = sheet.account_move_id.line_ids.filtered(
                lambda l: l.account_id.user_type_id.type in types)
            sheet.residual = abs(sum(lines.mapped('amount_residual')))
