# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.multi
    def action_cancel(self):
        for sheet in self:
            account_move = sheet.account_move_id
            sheet.account_move_id = False
            # If the sheet is paid then remove payments
            if sheet.state == 'done':
                payments = self.env['account.payment'].search([
                    ('expense_sheet_id', '=', sheet.id),
                    ('state', '!=', 'cancelled'),
                ])
                if sheet.expense_line_ids[:1].payment_mode == 'own_account':
                    self._remove_move_reconcile(payments, account_move)
                    self._cancel_payments(payments)
                else:
                    # In this case, during the cancellation the journal entry
                    # will be deleted
                    self._cancel_payments(payments)
                    payments.unlink()
            # Deleting the Journal entry if in the previous steps
            # (if the expense sheet is paid and payment_mode == 'own_account')
            # it has not been deleted
            if account_move.exists():
                if account_move.state != 'draft':
                    account_move.button_cancel()
                account_move.unlink()
            sheet.state = 'submit'

    @api.multi
    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        if self.expense_line_ids[0].payment_mode == 'company_account':
            self.account_move_id.mapped('line_ids.payment_id').write({
                'expense_sheet_id': self.id,
            })
        return res

    def _remove_move_reconcile(self, payments, account_move):
        """Delete only reconciliations made with the payments generated
        by hr_expense module automatically"""
        reconcile = account_move.mapped('line_ids.full_reconcile_id')

        payments_aml = payments.mapped('move_line_ids')
        aml_unreconcile = payments_aml.filtered(
            lambda r: r.full_reconcile_id in reconcile)

        aml_unreconcile.remove_move_reconcile()

    def _cancel_payments(self, payments):
        for rec in payments:
            for move in rec.move_line_ids.mapped('move_id'):
                move.button_cancel()
                move.unlink()
            rec.state = 'cancelled'
