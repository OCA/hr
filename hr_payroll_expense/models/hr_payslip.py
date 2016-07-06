# -*- coding: utf-8 -*-
# © 2016 Coninckx David (Open Net Sarl)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models, fields, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    expenses = fields.One2many('hr.expense', 'slip_id',
                               string='Expenses')

    @api.multi
    def compute_sheet(self):
        # Detach expenses from the pay slips
        ExpenseObj = self.env['hr.expense']
        expenses = ExpenseObj.search([('slip_id', 'in', self.ids)])
        if expenses:
            expenses.write({'slip_id': False})

        res = super(HrPayslip, self).compute_sheet()

        # Then, re-link the expenses

        for payslip in self:
            employee_id = payslip.contract_id.employee_id.id

            # Look for expenses
            filters = [
                ('employee_id', '=', employee_id),
                ('slip_id', '=', False),
                ('state', '=', ['done', 'post']),
            ]
            expenses = ExpenseObj.search(filters)
            if expenses:
                expenses.write({'slip_id': payslip.id})

        return res

    def process_sheet(self):
        ExpenseObj = self.env['hr.expense']
        expenses = ExpenseObj.search([
            ('slip_id', '=', self.id)
        ])
        for expense in expenses:
            expenses.state = 'done'
        return super(HrPayslip, self).process_sheet()
