# -*- coding: utf-8 -*-
# Copyright 2015 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2017 Vicent Cubells <vicent.cubells@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    invoice_id = fields.Many2one(
        comodel_name="account.invoice",
        string='Invoice',
        domain="[('type', '=', 'in_invoice'), ('state', '=', 'open')]",
        oldname='invoice',
    )

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        self.date = self.invoice_id.date_invoice
        self.name = self.invoice_id.number
        self.reference = self.invoice_id.number or self.invoice_id.reference
        self.analytic_account_id = False
        self.unit_amount = self.invoice_id.residual
        self.quantity = 1.0
        self.total_amount = self.unit_amount

    def _check_vals(self, vals):
        if vals.get('invoice_id'):
            # Rewrite values because readonly fields are not stored
            invoice = self.env['account.invoice'].browse(vals['invoice_id'])
            vals['date'] = invoice.date_invoice
            vals['analytic_account_id'] = False
            vals['unit_amount'] = invoice.residual
            vals['total_amount'] = invoice.residual
            vals['quantity'] = 1.0

    @api.model
    def create(self, vals):
        self._check_vals(vals)
        return super(HrExpense, self).create(vals)

    @api.multi
    def write(self, vals):
        self._check_vals(vals)
        return super(HrExpense, self).write(vals)

    def _prepare_move_line(self, line):
        expense = super(HrExpense, self)._prepare_move_line(line)
        if self.invoice_id and expense['debit']:
            expense['partner_id'] = \
                self.invoice_id.partner_id.commercial_partner_id.id
            expense['account_id'] = self.invoice_id.account_id.id
        return expense
