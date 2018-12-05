# Copyright 2018 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    analytic_tag_ids = fields.Many2many(
        comodel_name='account.analytic.tag',
        string='Analytic Tags',
        copy=True,
    )

    def _prepare_move_line(self, line):
        line_values = super(HrExpense, self)._prepare_move_line(line)
        if line_values.get('analytic_account_id'):
            tag_values = [[4, tag.id] for tag in self.analytic_tag_ids]
            line_values.update(analytic_tag_ids=tag_values)
        return line_values
