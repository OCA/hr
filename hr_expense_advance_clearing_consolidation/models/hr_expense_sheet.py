# Copyright 2022 - TODAY, Marcel Savegnago <marcel.savegnago@escodoo.com.br>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    is_consolidated_advance = fields.Boolean(
        string='Is Consolidated Advance',
        readonly=True
    )

    @api.multi
    def _consolidate_open_advances(self):
        if not len(self) > 1:
            raise UserError(
                _(
                    "To consolidate it is necessary to select more than one down payment."
                )
            )
        if len(self.mapped("employee_id")) != 1:
            raise UserError(
                _(
                    "You cannot consolidate advances from different employees. "
                    "Please select only advances from the same employee."
                )
            )
        if any(rec.clearing_residual <= 0 for rec in self):
            raise UserError(
                _("You cannot consolidate advances that do not have a balance.")
            )
        if any(rec.state != "done" for rec in self):
            raise UserError(_("You cannot consolidate advances that are not paid."))

        if self.env['hr.expense.sheet'].search(
            [
                ('advance', '=', False),
                ('state', '!=', 'done'),
                ('advance_sheet_id', 'in', self.ids)
            ]
        ):
            raise UserError(
                _(
                    "You cannot consolidate advances that are linked to an expense "
                    "report that is open."
                )
            )

        writeoff_lines = self.env["account.move.line"]
        emp_advance = self.env.ref("hr_expense_advance_clearing." "product_emp_advance")

        residual_value = 0
        for advance in self:
            for line in advance.sudo().account_move_id.line_ids:
                if line.account_id == emp_advance.property_account_expense_id:
                    residual_value += line.amount_residual
                    writeoff_acc_id = self.env["account.account"].search(
                        [("code", "=", line.counterpart)]
                    )
                    writeoff_journal_id = line.move_id.journal_id
                    line.reconcile(
                        writeoff_acc_id=writeoff_acc_id,
                        writeoff_journal_id=writeoff_journal_id,
                    )
                    for matched_credit_id in line.matched_credit_ids:
                        for (
                            move_line
                        ) in matched_credit_id.credit_move_id.move_id.line_ids:
                            if (
                                move_line.account_id.internal_type == "payable"
                                and not move_line.reconciled
                            ):
                                writeoff_lines |= move_line

        employee = advance.employee_id
        if residual_value > 0:
            consolidated_advance = self.env["hr.expense.sheet"].create(
                {
                    "name": "Consolidated Advance",
                    "employee_id": employee.id,
                    "is_consolidated_advance": True,
                }
            )
            consolidated_advance_line = self.env["hr.expense"].create(
                {
                    "name": "Consolidated Advance",
                    "employee_id": employee.id,
                    "product_id": emp_advance.id,
                    "unit_amount": residual_value,
                    "sheet_id": consolidated_advance.id,
                    "advance": True,
                }
            )
            consolidated_advance_line._onchange_product_id()
            consolidated_advance_line.unit_amount = residual_value

            # Submitted to Manager
            consolidated_advance.action_submit_sheet()
            # Approve
            consolidated_advance.approve_expense_sheets()
            # Create Expense Entries
            consolidated_advance.action_sheet_move_create()

            aml = self.env["account.move.line"]
            aml_to_reconcile = aml
            aml_to_reconcile_debit = aml
            aml_to_reconcile_credit = aml

            for line in writeoff_lines + consolidated_advance.account_move_id.line_ids:
                if line.account_id.internal_type == "payable" and not line.reconciled:
                    aml_to_reconcile |= line
                    if line.credit > 0:
                        aml_to_reconcile_credit |= line
                    if line.debit > 0:
                        aml_to_reconcile_debit |= line

            aml._reconcile_lines(
                aml_to_reconcile_debit,
                aml_to_reconcile_credit,
                "amount_residual_currency",
            )
            aml_to_reconcile.check_full_reconcile()
            consolidated_advance.set_to_paid()

            self._log_consolidation_open_advance(self, consolidated_advance)

            return consolidated_advance

    @api.multi
    def consolidate_open_advances(self):
        if self.env.user.has_group("account.group_account_manager"):
            self._consolidate_open_advances()
        else:
            raise UserError(
                _("You do not have permission to perform this action.")
            )

    @api.multi
    def _log_consolidation_open_advance(self, advances, consolidated_advance):
        consolidated_advance.message_post(body='%s %s' % (_("Consolidated advances:"), ", ".join('%s (ID %s)' % (p.name or 'n/a', p.id) for p in advances)))
        for advance in advances:
            advance.message_post(body='%s' % (_("This advance was consolidated in the advance: %s (ID %s)") % (consolidated_advance.name or 'n/a', consolidated_advance.id)))
