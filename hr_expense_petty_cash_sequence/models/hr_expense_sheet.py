# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    @api.model
    def create(self, vals):
        if 'expense_line_ids' in vals.keys():
            from_expense = vals['expense_line_ids'][0][1]
            if from_expense:
                expense = self.env['hr.expense'].browse(from_expense)
            else:
                from_report = vals['expense_line_ids'][0][2][0]
                expense = self.env['hr.expense'].browse(from_report)
            if vals.get('number', '/') == '/' and expense.payment_mode == 'petty_cash':
                number = self.env['ir.sequence'].next_by_code(
                    'hr.expense.sheet.petty.cash')
                vals['number'] = number
        return super(HrExpenseSheet, self).create(vals)
