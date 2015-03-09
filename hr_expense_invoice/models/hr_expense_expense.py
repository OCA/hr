# -*- encoding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in root directory
##############################################################################

from openerp import models, fields, api, exceptions, _


class HrExpenseExpense(models.Model):
    _inherit = 'hr.expense.expense'

    @api.model
    def line_get_convert(self, x, part, date):
        res = super(HrExpenseExpense, self).line_get_convert(x, part, date)
        if x.get('invoice'):
            res['partner_id'] = (
                x['invoice'].partner_id.commercial_partner_id.id)
        return res

    @api.model
    def move_line_get_item(self, line):
        if line.invoice:
            return {
                'account_id': line.invoice.account_id.id,
                'name': line.name,
                'price': line.total_amount,
                'invoice': line.invoice,
            }
        else:
            return super(HrExpenseExpense, self).move_line_get_item(line)

    @api.multi
    def action_move_create(self):
        """Reconcile supplier invoice payables with the created move lines."""
        res = super(HrExpenseExpense, self).action_move_create()
        for expense in self:
            for line in expense.line_ids:
                if line.invoice:
                    partner = line.invoice.partner_id.commercial_partner_id
                    move_lines = expense.account_move_id.line_id
                    c_move_lines = move_lines.filtered(
                        lambda x: x.partner_id == partner and
                        x.debit == line.invoice.residual)
                    c_move_lines |= line.invoice.move_id.line_id.filtered(
                        lambda x: x.account_id == line.invoice.account_id and
                        x.credit == line.invoice.residual)
                    if len(c_move_lines) != 2:
                        raise exceptions.Warning(
                            _('Cannot reconcile supplier invoice payable with '
                              'generated line. Please check amounts and see '
                              'if the invoice is already added or paid. '
                              'Invoice: %s') % line.invoice.name)
                    c_move_lines.reconcile()
        return res

    @api.multi
    def copy(self, default=None):
        res = super(HrExpenseExpense, self).copy(default)
        # Erase invoice references
        res.line_ids.write({'invoice': False})
        return res


class HrExpenseLine(models.Model):
    _inherit = 'hr.expense.line'

    invoice = fields.Many2one(
        comodel_name="account.invoice",
        domain="[('type', '=', 'in_invoice'), ('state', '=', 'open')]")

    @api.one
    @api.onchange('invoice')
    def onchange_invoice(self):
        """Show in screen invoice data"""
        self.product_id = False
        self.date_value = self.invoice.date_invoice
        self.name = self.invoice.number
        self.ref = (self.invoice.supplier_invoice_number or
                    self.invoice.reference)
        self.analytic_account = False
        self.unit_amount = self.invoice.residual
        self.unit_quantity = 1
        self.total_amount = self.unit_amount

    def _check_vals(self, vals):
        if vals.get('invoice'):
            # Rewrite values because readonly fields are not stored
            invoice = self.env['account.invoice'].browse(vals['invoice'])
            vals['product_id'] = False
            vals['date_value'] = invoice.date_invoice
            vals['analytic_account'] = False
            vals['unit_amount'] = invoice.residual
            vals['unit_quantity'] = 1

    @api.model
    def create(self, vals):
        self._check_vals(vals)
        return super(HrExpenseLine, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_vals(vals)
        return super(HrExpenseLine, self).write(vals)
