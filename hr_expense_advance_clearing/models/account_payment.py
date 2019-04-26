# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_counterpart_move_line_vals(self, invoice=False):
        emp_advance = self.env.ref('hr_expense_advance_clearing.'
                                   'product_emp_advance')
        res = super()._get_counterpart_move_line_vals(invoice=invoice)
        if self._context.get('hr_return_advance', False):
            res['account_id'] = emp_advance.property_account_expense_id.id
        return res
