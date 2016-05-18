# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # ---------- Fields management

    invoices = fields.One2many('account.invoice', 'slip_id',
                               string='Invoices')
    move_lines = fields.One2many('account.move.line', 'slip_id',
                                 string='Journal Items')

    # ---------- Utilities

    @api.multi
    def compute_sheet(self):

        # First, detach invoices from the pay slips
        InvoiceObj = self.env['account.invoice']
        invoices = InvoiceObj.search([('slip_id', 'in', self.ids)])
        if invoices:
            invoices.write({'slip_id': False})

        # Second, detach account move lines from the pay slips
        AccountMoveLineObj = self.env['account.move.line']
        aml = AccountMoveLineObj.search([('slip_id', 'in', self.ids)])
        if aml:
            aml.write({'slip_id': False})

        res = super(HrPayslip, self).compute_sheet()

        # Then, re-link the invoices, the expenses
        # and the account move lines using the criterias
        InvoiceLineObj = self.env['account.invoice.line']
        for payslip in self:
            # No contract? forget about it
            if not payslip.contract_id:
                continue

            # No user? forget about it
            user_id = payslip.contract_id.employee_id.user_id.id
            if not user_id:
                continue

            # Look for invoice lines
            inv_ids = []
            filters = [
                ('invoice_id.user_id', '=', user_id),
                ('product_id', '!=', False),
                ('invoice_id.state', 'in', ['open', 'paid']),
                ('invoice_id.type', '=', 'out_invoice'),
            ]
            move_ids = []
            for invl in InvoiceLineObj.search(filters):
                if invl.invoice_id.id not in inv_ids:
                    inv_ids.append(invl.invoice_id.id)
                    invl.invoice_id.write({'slip_id': payslip.id})
                if invl.invoice_id.move_id and \
                        invl.invoice_id.move_id.id not in move_ids:
                    move_ids.append(str(invl.invoice_id.move_id.id))

            inv_lines = InvoiceLineObj.search(filters)
            invoices = inv_lines.mapped('invoice_id')
            invoices.write({'slip_id': payslip.id})
            moves = invoices.mapped('move_id')

            # Look for account move lines
            if moves:
                move_line_ids = self.env["account.move.line"].search([
                    ('move_id', 'in', moves.ids),
                    ('reconciled', '=', True),
                    ('slip_id', '=', False)]
                ).ids

                if move_line_ids:
                    move_line_ids = [str(id) for id in move_line_ids]
                    q = """update account_move_line
    set slip_id=%d where id in (%s)""" % (payslip.id, ','.tuple(move_line_ids))
                    self.env.cr.execute(q)

        return res
