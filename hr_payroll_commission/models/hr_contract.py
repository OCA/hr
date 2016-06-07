# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class HrContract(models.Model):
    _inherit = 'hr.contract'

    # ---------- Fields management
    commission = fields.Float(string='Commission',
                              compute='_comp_commission')
    comm_rate = fields.Float(string='Commissions Rate',
                             digits=dp.get_precision('Payroll Rate'))

    @api.multi
    @api.depends('employee_id.user_id')
    def _comp_commission(self):
        for contract in self:
            contract.commission = 0

            account_invoice_obj = self.env['account.invoice']
            invoice_ids = account_invoice_obj.search([
                ('state', 'in', ('open', 'paid')),
                ('user_id', '=', contract.employee_id.user_id.id),
                ('type', '=', 'out_invoice'),
                ('slip_id', '=', False)
            ])

            # Compute comission based
            commission = 0
            for invoice_id in invoice_ids:
                for move_line in invoice_id.payment_move_line_ids:
                    if not move_line.slip_id.id:
                        commission += move_line.credit
            contract.commission = commission
