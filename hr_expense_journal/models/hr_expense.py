# Copyright (C) 2021 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    payment_type_id = fields.Many2one("account.journal", string="Payment Journal")

    def _create_sheet_from_expenses(self):
        res = super()._create_sheet_from_expenses()
        if self.payment_type_id:
            res.update({"bank_journal_id": self.payment_type_id.id})
        return res
