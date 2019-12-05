# Copyright 2019 Ecosoft <saranl@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_cash_basis_matched_percentage(self):
        res = super()._get_cash_basis_matched_percentage()
        if (
            res == 1
            and self._context.get("use_hr_expense_invoice")
            and self._context.get("default_expense_line_ids")
        ):
            return False
        return res
