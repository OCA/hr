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
        for contract in self:
            contract.reimbursement = 0

            # Look in linked expenses:
            filters = [
                ('employee_id', '=', contract.employee_id.id),
                ('slip_id', '=', False),
                ('state', 'in', ['done', 'post']),
            ]

            # Compute reimbursement
            reimbursement = 0
            ExpensesObj = self.env['hr.expense']
            for expense in ExpensesObj.search(filters):
                reimbursement += expense.account_move_id.amount
            contract.reimbursement += reimbursement
