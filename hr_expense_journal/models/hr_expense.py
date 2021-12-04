# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    payment_type_id = fields.Many2one("account.journal", string="Payment Journal")

    def action_submit_expenses(self):
        res = super().action_submit_expenses()
        if self[0].payment_type_id:
            res['context'].update(
                {'default_bank_journal_id': self[0].payment_type_id.id}
            )
        return res
