# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    reimbursement = fields.Float(string='Reimbursement',
                                 compute='_comp_reimbursement')

    @api.multi
    @api.depends('employee_id.user_id')
    def _comp_reimbursement(self):
        ExpensesObj = self.env['hr.expense']
        for contract in self:
            # Look in linked expenses:
            filters = [
                ('employee_id', '=', contract.employee_id.id),
                ('slip_id', '=', False),
                ('state', '=', 'approve'),
            ]

            # Compute reimbursement
            reimbursement = 0
            for expense in ExpensesObj.search(filters):
                amount = expense.total_amount
                reimbursement = reimbursement + amount
            contract.reimbursement = reimbursement
