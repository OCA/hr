# Copyright 2015 Tecnativa - Pedro M. Baeza
# Copyright 2017 Tecnativa - Vicent Cubells
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    invoice_count = fields.Integer(
        compute='_compute_invoice_count',
    )

    @api.multi
    def action_sheet_move_create(self):
        expense_line_ids = \
            self.mapped('expense_line_ids').filtered('invoice_id')
        self._validate_expense_invoice(expense_line_ids)
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        for sheet in self:
            move_lines = res[sheet.id].line_ids
            expense_line_ids = self.expense_line_ids.filtered('invoice_id')
            c_move_lines = self.env['account.move.line']
            for line in expense_line_ids:
                partner = line.invoice_id.partner_id.commercial_partner_id
                c_move_lines |= move_lines.filtered(
                    lambda x:
                    x.partner_id == partner and x.debit and not x.reconciled)
                c_move_lines |= line.invoice_id.move_id.line_ids.filtered(
                    lambda x:
                    x.account_id == line.invoice_id.account_id
                    and x.credit and not x.reconciled)
            c_move_lines.reconcile()
        return res

    @api.multi
    def _compute_invoice_count(self):
        Invoice = self.env['account.invoice']
        can_read = Invoice.check_access_rights('read', raise_exception=False)
        for sheet in self:
            sheet.invoice_count = can_read and \
                len(sheet.expense_line_ids.mapped('invoice_id')) or 0

    @api.model
    def _validate_expense_invoice(self, expense_lines):
        DecimalPrecision = self.env['decimal.precision']
        precision = DecimalPrecision.precision_get('Product Price')
        invoices = expense_lines.mapped('invoice_id')
        if not invoices:
            return
        # All invoices must confirmed
        if any(invoices.filtered(lambda i: i.state != 'open')):
            raise UserError(_('Vendor bill state must be Open'))
        expense_amount = sum(expense_lines.mapped('total_amount'))
        invoice_amount = sum(invoices.mapped('residual'))
        # Expense amount must equal invoice amount
        if float_compare(expense_amount, invoice_amount, precision) != 0:
            raise UserError(
                _('Vendor bill amount mismatch!\nPlease make sure amount in '
                  'vendor bills equal to amount of its expense lines'))

    @api.multi
    def action_view_invoices(self):
        self.ensure_one()
        action = {
            'name': _('Invoices'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.invoice',
            'target': 'current',
        }
        invoice_ids = self.expense_line_ids.mapped('invoice_id').ids
        view = self.env.ref('account.invoice_supplier_form')
        if len(invoice_ids) == 1:
            invoice = invoice_ids[0]
            action['res_id'] = invoice
            action['view_mode'] = 'form'
            action['views'] = [(view.id, 'form')]
        else:
            action['view_mode'] = 'tree,form'
            action['domain'] = [('id', 'in', invoice_ids)]
        return action
