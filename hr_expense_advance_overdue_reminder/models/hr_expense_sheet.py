# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta
from odoo import api, models, fields, _
from odoo.exceptions import UserError

payment_mode_list = {
    'own_account': 'Employee (to reimburse)',
    'company_account': 'Company'
}


class HrExpenseSheet(models.Model):
    _inherit = 'hr.expense.sheet'

    no_overdue_reminder = fields.Boolean(
        string='Disable Overdue Reminder',
        track_visibility='onchange')
    overdue_reminder_ids = fields.One2many(
        comodel_name='hr.expense.sheet.overdue.reminder',
        inverse_name='expense_sheet_id',
        string='Overdue Reminder Action History')
    overdue_reminder_last_date = fields.Date(
        compute='_compute_overdue_reminder',
        string='Last Overdue Reminder Date', store=True)
    overdue_reminder_counter = fields.Integer(
        string='Overdue Reminder Count', store=True,
        compute='_compute_overdue_reminder',
        help="This counter is not increased in case of phone reminder.")
    overdue = fields.Boolean(compute='_compute_overdue')
    date_due = fields.Date(string='Due Date', readonly=True)

    _sql_constraints = [(
        'counter_positive',
        'CHECK(overdue_reminder_counter >= 0)',
        'Overdue Invoice Counter must always be positive')]

    @api.depends('state', 'date_due')
    def _compute_overdue(self):
        today = fields.Date.context_today(self)
        for exp in self:
            if exp.advance and exp.state == 'done' and exp.date_due and \
                    exp.date_due < today:
                exp.overdue = True

    @api.depends(
        'overdue_reminder_ids.action_id.date',
        'overdue_reminder_ids.counter',
        'overdue_reminder_ids.action_id.reminder_type')
    def _compute_overdue_reminder(self):
        advance_overdue_object = \
            self.env['hr.expense.sheet.overdue.reminder']
        for exp in self:
            reminder = advance_overdue_object.search(
                [('expense_sheet_id', '=', exp.id)], order='action_date desc',
                limit=1)
            date = reminder and reminder.action_date or False
            counter_reminder = advance_overdue_object.search([
                ('expense_sheet_id', '=', exp.id),
                ('action_reminder_type', 'in', ('mail', 'post'))],
                order='action_date desc, id desc', limit=1)
            counter = counter_reminder and counter_reminder.counter or False
            exp.overdue_reminder_last_date = date
            exp.overdue_reminder_counter = counter

    @api.multi
    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        company = self.env.user.company_id
        for sheet in self:
            if res and sheet.advance:
                move_date = res[sheet.id].date
                sheet.date_due = move_date + relativedelta(
                    days=company.terms_date_due_days)
        return res

    @api.multi
    def action_overdue_reminder(self):
        today = fields.Date.today()
        expense_not_overdue = self.filtered(lambda exp: not (
            exp.residual and exp.advance and exp.date_due < today
            and exp.state == 'done'))
        if expense_not_overdue:
            raise UserError(_("You cannot remind this report."))
        partner_ids = [expense.address_id.id for expense in self]
        return {
            'name': _('New Overdue Advance Letter'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hr.advance.overdue.reminder.wizard',
            'target': 'new',
            'context': {
                'default_partner_ids': partner_ids,
                'overdue_sheet_ids': self._context.get('active_ids', False),
            }
        }

    @api.multi
    def get_payment_mode(self, payment_mode):
        self.ensure_one()
        return payment_mode_list[payment_mode]
