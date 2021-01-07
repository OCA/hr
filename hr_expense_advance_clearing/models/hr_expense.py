# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    advance = fields.Boolean(
        string='Employee Advance',
        default=False,
    )

    @api.multi
    @api.constrains('advance')
    def _check_advance(self):
        for expense in self.filtered('advance'):
            emp_advance = self.env.ref('hr_expense_advance_clearing.'
                                       'product_emp_advance')
            if not emp_advance.property_account_expense_id:
                raise ValidationError(
                    _('Employee advance product has no payable account'))
            if expense.product_id != emp_advance:
                raise ValidationError(
                    _('Employee advance, selected product is not valid'))
            if expense.tax_ids:
                raise ValidationError(
                    _('Employee advance, all taxes must be removed'))
            if expense.payment_mode != 'own_account':
                raise ValidationError(
                    _('Employee advance, paid by must be employee'))
        return True

    @api.onchange('advance')
    def onchange_advance(self):
        self.tax_ids = False
        self.payment_mode = 'own_account'
        if self.advance:
            self.product_id = self.env.ref(
                'hr_expense_advance_clearing.product_emp_advance')
        else:
            self.product_id = False

    @api.multi
    def _get_account_move_line_values(self):
        move_line_values_by_expense = super()._get_account_move_line_values()
        # Only when do the clearing, change cr payable to cr advance
        emp_advance = self.env.ref('hr_expense_advance_clearing.'
                                   'product_emp_advance')
        sheets = self.mapped('sheet_id').filtered('advance_sheet_id')
        sheets_x = sheets.filtered(lambda x: x.advance_sheet_residual <= 0.0)
        if sheets_x:  # Advance Sheets with no clearing residual left
            raise ValidationError(_('Advance: %s has no amount to clear') %
                                  ', '.join(sheets_x.mapped('name')))
        for sheet in sheets:
            advance_to_clear = sheet.advance_sheet_residual
            for expense_id, move_lines in move_line_values_by_expense.items():
                payable_move_line = False
                for move_line in move_lines:
                    credit = move_line['credit']
                    if not credit:
                        continue
                    # cr payable -> cr advance
                    remain_payable = 0.0
                    if credit > advance_to_clear:
                        remain_payable = credit - advance_to_clear
                        move_line['credit'] = advance_to_clear
                        advance_to_clear = 0.0
                        # extra payable line
                        payable_move_line = move_line.copy()
                        payable_move_line['credit'] = remain_payable
                    else:
                        advance_to_clear -= credit
                    # advance line
                    move_line['account_id'] = \
                        emp_advance.property_account_expense_id.id
                if payable_move_line:
                    move_lines.append(payable_move_line)
        return move_line_values_by_expense
