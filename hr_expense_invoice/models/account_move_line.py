# Copyright 2019 Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def reconcile(self, writeoff_acc_id=False, writeoff_journal_id=False):
        if self._context.get('use_hr_expense_invoice'):
            self = self.filtered(lambda l: not l.reconciled)
        res = super().reconcile(writeoff_acc_id=writeoff_acc_id,
                                writeoff_journal_id=writeoff_journal_id)
        return res
