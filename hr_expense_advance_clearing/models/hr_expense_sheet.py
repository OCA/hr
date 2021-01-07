# Copyright 2019 Kitti Upariphutthiphong <kittiu@ecosoft.co.th>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools import pycompat
from odoo.exceptions import ValidationError


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    advance = fields.Boolean(
        string='Employee Advance',
        compute='_compute_advance',
        store=True,
    )
    advance_sheet_id = fields.Many2one(
        comodel_name='hr.expense.sheet',
        string='Clear Advance',
        domain="[('advance', '=', True), ('employee_id', '=', employee_id),"
               " ('clearing_residual', '>', 0.0)]",
        readonly=True,
        states={'draft': [('readonly', False)],
                'submit': [('readonly', False)],
                'approve': [('readonly', False)]},
        help="Show remaining advance of this employee",
    )
    clearing_residual = fields.Monetary(
        string='Amount to clear',
        compute='_compute_clearing_residual',
        store=True,
        help="Amount to clear of this expense sheet in company currency",
    )
    advance_sheet_residual = fields.Monetary(
        string='Advance Remaining',
        related='advance_sheet_id.clearing_residual',
        store=True,
        help="Remaining amount to clear the selected advance sheet",
    )
    amount_payable = fields.Monetary(
        string='Payable Amount',
        compute='_compute_amount_payable',
        help="Final regiter payment amount even after advance clearing",
    )

    @api.multi
    @api.depends('expense_line_ids')
    def _compute_advance(self):
        for sheet in self:
            sheet.advance = bool(sheet.expense_line_ids.filtered('advance') and
                                 len(sheet.expense_line_ids) == 1)
        return

    @api.one
    @api.constrains('advance_sheet_id', 'expense_line_ids')
    def _check_advance_expense(self):
        advance_lines = self.expense_line_ids.filtered('advance')
        if self.advance_sheet_id and advance_lines:
            raise ValidationError(_('Advance clearing must not contain any '
                                    'advance expense line'))
        if advance_lines and len(self.expense_line_ids) != 1:
            raise ValidationError(_('Advance must contain only 1 '
                                    'advance expense line'))

    @api.one
    @api.depends('account_move_id.line_ids.amount_residual')
    def _compute_clearing_residual(self):
        residual_company = 0.0
        emp_advance = self.env.ref('hr_expense_advance_clearing.'
                                   'product_emp_advance', False)
        if emp_advance:
            for line in self.sudo().account_move_id.line_ids:
                if line.account_id == emp_advance.property_account_expense_id:
                    residual_company += line.amount_residual
        self.clearing_residual = residual_company

    @api.multi
    def _compute_amount_payable(self):
        for sheet in self:
            rec_lines = sheet.account_move_id.line_ids.filtered(
                lambda x:
                x.credit and x.account_id.reconcile and not x.reconciled)
            sheet.amount_payable = -sum(rec_lines.mapped('amount_residual'))

    @api.multi
    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        # Reconcile advance of this sheet with the advance_sheet
        emp_advance = self.env.ref('hr_expense_advance_clearing.'
                                   'product_emp_advance')
        for sheet in self:
            move_lines = sheet.account_move_id.line_ids | \
                sheet.advance_sheet_id.account_move_id.line_ids
            account_id = emp_advance.property_account_expense_id.id
            adv_move_lines = self.env['account.move.line'].sudo().search([
                ('id', 'in', move_lines.ids), ('account_id', '=', account_id)])
            adv_move_lines.reconcile()
        return res

    @api.multi
    def open_clear_advance(self):
        self.ensure_one()
        action = self.env.ref('hr_expense_advance_clearing.'
                              'action_hr_expense_sheet_advance_clearing')
        vals = action.read()[0]
        context1 = vals.get('context', {})
        if isinstance(context1, pycompat.string_types):
            context1 = safe_eval(context1)
        context1['default_advance_sheet_id'] = self.id
        vals['context'] = context1
        return vals
