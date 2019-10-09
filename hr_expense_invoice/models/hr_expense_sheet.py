# -*- coding: utf-8 -*-
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, models
from odoo.tools import float_compare


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    @api.multi
    def action_sheet_move_create(self):
        precision = self.env['decimal.precision'].precision_get('Account')
        expense_line_ids = self.mapped('expense_line_ids').filtered(
            lambda r: r.invoice_id,
        )
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        move_lines = self.env['account.move'].search(
            [('ref', 'in', self.mapped('name'))],
        ).mapped('line_ids')
        for line in expense_line_ids:
            partner = line.invoice_id.partner_id.commercial_partner_id
            c_move_lines = move_lines.filtered(
                lambda x:
                x.partner_id == partner and
                x.debit == line.invoice_id.residual and
                not x.reconciled
            )
            if len(c_move_lines) > 1:
                c_move_lines = c_move_lines[0]
            residual = line.invoice_id.residual
            c_move_lines |= line.invoice_id.move_id.line_ids.filtered(
                lambda x:
                x.account_id == line.invoice_id.account_id and
                float_compare(x.credit, residual, precision) == 0)
            if len(c_move_lines) != 2:
                raise exceptions.Warning(
                    _('Cannot reconcile supplier invoice payable with '
                      'generated line. Please check amounts and see '
                      'if the invoice is already added or paid. '
                      'Invoice: %s') % line.invoice_id.number)
            c_move_lines.reconcile()
        return res
