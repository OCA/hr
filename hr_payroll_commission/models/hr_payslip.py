# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # ---------- Fields management

    invoice_ids = fields.One2many(
        'account.invoice', 'slip_id',
        string='Invoices')
    move_line_ids = fields.One2many(
        'account.move.line', 'slip_id',
        string='Journal Items')

    # ---------- Utilities

    def _detach_invoices_from_payslip(self):
        InvoiceObj = self.env['account.invoice']
        invoices = InvoiceObj.search([('slip_id', 'in', self.ids)])
        if invoices:
            invoices.write({'slip_id': False})

    def _detach_move_lines_from_payslip(self):
        AccountMoveLineObj = self.env['account.move.line']
        aml = AccountMoveLineObj.search([('slip_id', 'in', self.ids)])
        if aml:
            aml.write({'slip_id': False})

    def _attach_invoices_to_payslip(self):
        account_invoice_obj = self.env['account.invoice']
        invoice_ids = account_invoice_obj.search([
            ('state', 'in', ('open', 'paid')),
            ('user_id', '=', self.employee_id.user_id.id),
            ('type', '=', 'out_invoice'),
            ('slip_id', '=', False)
        ])
        invoice_ids.write({'slip_id': self.id})
        return invoice_ids

    def _attach_move_lines_to_payslip(self, invoices):
        for invoice in invoices:
            invoice.payment_move_line_ids.write(
                {'slip_id': self.id}
            )

    @api.multi
    def compute_sheet(self):
        self._detach_invoices_from_payslip()
        self._detach_move_lines_from_payslip()

        res = super(HrPayslip, self).compute_sheet()

        # Then, re-link the invoices, the expenses
        # and the account move lines using the criterias
        for payslip in self:
            # No contract? forget about it
            if not payslip.contract_id:
                continue

            invoice_ids = self._attach_invoices_to_payslip()
            self._attach_move_lines_to_payslip(invoice_ids)

        return res
