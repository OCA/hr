# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _create_payment_entry(self, amount):
        if self._context.get('active_model') == 'hr.expense.sheet' and \
                self._context.get('default_amount'):
            self.payment_difference = \
                amount - self._context.get('default_amount')
        return super()._create_payment_entry(amount)
