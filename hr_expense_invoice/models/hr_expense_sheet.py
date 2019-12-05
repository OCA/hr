# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_compare


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    invoice_count = fields.Integer(compute="_compute_invoice_count")
    invoice_fully_created = fields.Boolean(compute="_compute_invoice_count")

    def action_sheet_move_create(self):
        expense_line_ids = self.mapped("expense_line_ids").filtered("invoice_id")
        self._validate_expense_invoice(expense_line_ids)
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        for sheet in self:
            move_lines = res[sheet.id].line_ids
            expense_line_ids = self.expense_line_ids.filtered("invoice_id")
            c_move_lines = self.env["account.move.line"]
            for line in expense_line_ids:
                partner = line.invoice_id.partner_id.commercial_partner_id
                c_move_lines |= move_lines.filtered(
                    lambda x: x.partner_id == partner and x.debit and not x.reconciled
                )
                c_move_lines |= line.invoice_id.line_ids.filtered(
                    lambda x: x.account_id
                    == line.invoice_id.line_ids.filtered(
                        lambda l: l.account_internal_type == "payable"
                    ).account_id
                    and x.credit
                    and not x.reconciled
                )
            c_move_lines.with_context(use_hr_expense_invoice=True).reconcile()
        return res

    def _compute_invoice_count(self):
        Invoice = self.env["account.move"]
        can_read = Invoice.check_access_rights("read", raise_exception=False)
        for sheet in self:
            sheet.invoice_count = (
                can_read and len(sheet.expense_line_ids.mapped("invoice_id")) or 0
            )
            sheet.invoice_fully_created = not any(
                self.mapped("expense_line_ids").filtered(lambda l: not l.invoice_id)
            )

    @api.model
    def _validate_expense_invoice(self, expense_lines):
        DecimalPrecision = self.env["decimal.precision"]
        precision = DecimalPrecision.precision_get("Product Price")
        invoices = expense_lines.mapped("invoice_id")
        if not invoices:
            return
        # All invoices must confirmed
        if any(invoices.filtered(lambda i: i.state != "posted")):
            raise UserError(_("Vendor bill state must be Posted"))
        expense_amount = sum(expense_lines.mapped("total_amount"))
        invoice_amount = sum(invoices.mapped("amount_residual"))
        # Expense amount must equal invoice amount
        if float_compare(expense_amount, invoice_amount, precision) != 0:
            raise UserError(
                _(
                    "Vendor bill amount mismatch!\nPlease make sure amount in "
                    "vendor bills equal to amount of its expense lines"
                )
            )

    def action_view_invoices(self):
        self.ensure_one()
        action = {
            "name": _("Invoices"),
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "target": "current",
        }
        invoice_ids = self.expense_line_ids.mapped("invoice_id").ids
        view = self.env.ref("account.view_move_form")
        if len(invoice_ids) == 1:
            invoice = invoice_ids[0]
            action["res_id"] = invoice
            action["view_mode"] = "form"
            action["views"] = [(view.id, "form")]
        else:
            action["view_mode"] = "tree,form"
            action["domain"] = [("id", "in", invoice_ids)]
        return action
