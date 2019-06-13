# Copyright 2019 Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = 'hr.expense.sheet.register.payment.wizard'

    @api.multi
    def expense_post_payment(self):
        self = self.with_context(use_hr_expense_invoice=True)
        return super().expense_post_payment()
