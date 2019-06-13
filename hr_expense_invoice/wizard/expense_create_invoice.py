# Copyright 2019 Kitti U. <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HRExpenseCreateInvoice(models.TransientModel):
    _name = 'hr.expense.create.invoice'
    _description = 'Create invoice from expense report'

    expense_ids = fields.Many2many(
        comodel_name='hr.expense',
        string='Expenses',
        domain=lambda self: self._domain_expense_ids(),
        required=True,
    )

    @api.model
    def view_init(self, fields):
        active_id = self._context.get('active_id')
        sheet = self.env['hr.expense.sheet'].browse(active_id)
        if sheet.state != 'approve':
            raise UserError(_('This action is allowed only in Approved sate'))
        return super().view_init(fields)

    @api.model
    def _domain_expense_ids(self):
        active_id = self._context.get('active_id')
        sheet = self.env['hr.expense.sheet'].browse(active_id)
        domain = [('id', 'in', sheet.expense_line_ids.ids),
                  ('invoice_id', '=', False)]
        return domain

    @api.multi
    def create_invoice(self):
        """Use information from selected invoice to create invoice."""
        self.ensure_one()
        expenses = self.expense_ids.filtered(lambda l: not l.invoice_id)
        if not expenses:
            raise UserError(_('No valid expenses to create invoice'))
        expense = expenses[0]
        invoice_lines = [
            (0, 0, {'product_id': x.product_id.id,
                    'name': x.name,
                    'price_unit': x.unit_amount,
                    'quantity': x.quantity,
                    'date_invoice': x.date,
                    'account_id': x.account_id.id,
                    'invoice_line_tax_ids': [(6, 0, x.tax_ids.ids)], })
            for x in expenses
        ]
        invoice_vals = {
            'type': 'in_invoice',
            'journal_type': 'purchase',
            'reference': expense.reference,
            'date_invoice': expense.date,
            'invoice_line_ids': invoice_lines, }
        invoice = self.env['account.invoice'].create(invoice_vals)
        self.expense_ids.write({'invoice_id': invoice.id})
        return invoice
