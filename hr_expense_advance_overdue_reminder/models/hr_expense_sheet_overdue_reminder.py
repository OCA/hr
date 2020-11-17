# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrExpenseSheetOverdueReminder(models.Model):
    _name = 'hr.expense.sheet.overdue.reminder'
    _inherit = 'account.invoice.overdue.reminder'
    _description = 'Expense Sheet Overdue Reminder'

    expense_sheet_id = fields.Many2one(
        comodel_name='hr.expense.sheet', string='Expense Sheet',
        ondelete='cascade', readonly=True
    )
    action_id = fields.Many2one(
        comodel_name='advance.overdue.reminder.action',
        string='Overdue Reminder Action',
        ondelete='cascade')
    company_id = fields.Many2one(
        related='expense_sheet_id.company_id', store=True)

    @api.constrains('expense_sheet_id')
    def expense_sheet_id_check(self):
        for action in self:
            if action.expense_sheet_id and not action.expense_sheet_id.advance:
                raise ValidationError(_(
                    "An overdue reminder can only be attached "
                    "to a employee advance."))

    @api.depends('expense_sheet_id', 'counter')
    def name_get(self):
        res = []
        for rec in self:
            name = _('%s Reminder %d') % (
                rec.expense_sheet_id.name, rec.counter)
            res.append((rec.id, name))
        return res
