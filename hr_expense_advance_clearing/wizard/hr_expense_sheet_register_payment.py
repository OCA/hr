# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.urls import url_encode

from odoo import _, api, models


class HrExpenseSheetRegisterPaymentWizard(models.TransientModel):
    _inherit = "hr.expense.sheet.register.payment.wizard"

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        ctx = self._context.copy()
        sheet = self.env["hr.expense.sheet"].browse(ctx.get("active_id"))
        if ctx.get("hr_return_advance", False):
            res.update({"amount": sheet.residual})
        else:
            res.update({"amount": sheet.amount_payable})
        return res

    def expense_post_payment(self):
        if self._context.get("hr_return_advance", False):
            return self.expense_post_return_advance()
        return super().expense_post_payment()

    def expense_post_return_advance(self):
        """ This is opposite operation of expense_post_payment(),
        it return remaining advance from employee back to company
        """
        self.ensure_one()
        context = dict(self._context or {})
        active_ids = context.get("active_ids", [])
        expense_sheet = self.env["hr.expense.sheet"].browse(active_ids)
        emp_advance = self.env.ref("hr_expense_advance_clearing." "product_emp_advance")
        advance_account = emp_advance.property_account_expense_id

        # Create return advance and post it
        payment = self.env["account.payment"].create(self._get_payment_vals())
        # Set new payment_type and payment entry to be Dr Bank, Cr Advance
        payment.payment_type = "inbound"
        payment.partner_type = "customer"
        payment.destination_account_id = advance_account
        payment.post()

        # Log the return advance in the chatter
        body = _(
            "A remaining advance return of %s %s with the reference "
            "<a href='/mail/view?%s'>%s</a> related to your expense %s "
            "has been made."
        ) % (
            payment.amount,
            payment.currency_id.symbol,
            url_encode({"model": "account.payment", "res_id": payment.id}),
            payment.name,
            expense_sheet.name,
        )
        expense_sheet.message_post(body=body)

        # Reconcile the return advance and the advance,
        # i.e. lookup on the advance account on move lines
        account_move_lines_to_reconcile = self.env["account.move.line"]
        for line in payment.move_line_ids + expense_sheet.account_move_id.line_ids:
            if line.account_id == advance_account:
                account_move_lines_to_reconcile |= line
        account_move_lines_to_reconcile.reconcile()

        return {"type": "ir.actions.act_window_close"}
