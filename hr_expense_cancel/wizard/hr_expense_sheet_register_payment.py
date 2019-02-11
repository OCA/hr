# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"

    def _get_payment_vals(self):
        sup = super(HrExpenseSheetRegisterPaymentWizard, self)
        res = sup._get_payment_vals()
        expense_sheet = self.env.context.get('active_ids')
        if len(expense_sheet) == 1:
            res.update(expense_sheet_id=expense_sheet[0])
        return res
