# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    invoice_id = fields.Many2one(
        comodel_name='account.invoice',
        string='Vendor Bill',
        domain="[('type', '=', 'in_invoice'), ('state', '=', 'open')]",
        oldname='invoice',
        copy=False,
    )

    @api.multi
    @api.constrains('invoice_id')
    def _check_invoice_id(self):
        for expense in self:  # Only non binding expense
            if not expense.sheet_id and expense.invoice_id and \
                    expense.invoice_id.state != 'open':
                raise UserError(_("Vendor bill state must be Open"))

    @api.multi
    def _get_account_move_line_values(self):
        move_line_values_by_expense = super()._get_account_move_line_values()
        for expense_id, move_lines in move_line_values_by_expense.items():
            expense = self.browse(expense_id)
            if not expense.invoice_id:
                return move_line_values_by_expense
            for move_line in move_lines:
                if move_line['debit']:
                    move_line['partner_id'] = \
                        expense.invoice_id.partner_id.commercial_partner_id.id
                    move_line['account_id'] = expense.invoice_id.account_id.id
        return move_line_values_by_expense
