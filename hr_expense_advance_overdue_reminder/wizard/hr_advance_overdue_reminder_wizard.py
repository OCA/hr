# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
logger = logging.getLogger(__name__)

MOD = 'hr_expense_advance_overdue_reminder'


class HrAdvanceOverdueReminderWizard(models.TransientModel):
    _name = 'hr.advance.overdue.reminder.wizard'
    _inherit = 'overdue.reminder.start'
    _description = 'Reminder Overdue Advance'

    partner_ids = fields.Many2many(domain=[])

    payment_ids = fields.Many2many(
        comodel_name='hr.advance.overdue.start.payment',
        relation='advance_wizard_id',
        readonly=True
    )
    interface = fields.Selection(default='mass', readonly=True)

    def _prepare_base_domain(self):
        base_domain = [
            ('company_id', '=', self.company_id.id),
            ('advance', '=', True),
            ('state', '=', 'done'),
            ('residual', '>', 0.0),
            ('no_overdue_reminder', '=', False),
            ]
        return base_domain

    def _prepare_remind_trigger_domain(self, base_domain):
        today = fields.Date.context_today(self)
        limit_date = today
        if self.start_days:
            limit_date -= relativedelta(days=self.start_days)
        domain = base_domain + [('date_due', '<', limit_date)]
        if self.partner_ids:
            domain.append(('address_id', 'in', self.partner_ids.ids))
        return domain

    def _prepare_reminder_step(
            self, partner, base_domain, min_interval_date, sale_journals):
        moveline_object = self.env['account.move.line']
        expense_sheet_object = self.env['hr.expense.sheet']
        if partner.no_overdue_reminder:
            logger.info(
                'Skipping customer %s that has no_overdue_reminder=True',
                partner.display_name)
            return False
        overdue_sheet_ids = self._context.get('overdue_sheet_ids', False)
        if overdue_sheet_ids:
            print(overdue_sheet_ids)
            print("====")
            expense_sheet_ids = expense_sheet_object.browse(overdue_sheet_ids)
            expense_sheet_ids = expense_sheet_ids.filtered(
                lambda l: l.address_id.id == partner.id)
        else:
            expense_sheet_ids = expense_sheet_object.search(
                base_domain + [
                    ('address_id', '=', partner.id),
                    ('date_due', '<', fields.Date.context_today(self)),
                    # Check min interval
                    '|', ('overdue_reminder_last_date', '=', False),
                    ('overdue_reminder_last_date', '<=', min_interval_date)
                    ])
        if not expense_sheet_ids:
            return False
        max_counter = max(
            [exp.overdue_reminder_counter for exp in expense_sheet_ids])
        warn_unrec = moveline_object.search([
            ('account_id', '=',
                partner.commercial_partner_id.property_account_receivable_id.id
             ),
            ('expense_id', '!=', False),
            ('partner_id', '=', partner.commercial_partner_id.id),
            ('full_reconcile_id', '=', False),
            ('matched_debit_ids', '=', False),
            ('matched_credit_ids', '=', False),
            ('journal_id', 'in', sale_journals.ids)
        ])
        vals = {
            'partner_id': expense_sheet_ids[0].address_id.id,
            'commercial_partner_id': partner.id,
            'user_id': self.env.user.id,
            'expense_sheet_ids': [(6, 0, expense_sheet_ids.ids)],
            'company_id': self.company_id.id,
            'warn_unreconciled_move_line_ids': [(6, 0, warn_unrec.ids)],
            'counter': max_counter + 1,
            'interface': self.interface,
            }
        return vals

    def run(self):
        self.ensure_one()
        if not self.up_to_date:
            raise UserError(_(
                "In order to start overdue reminders, you must make sure that "
                "customer payments are up-to-date."))
        if self.start_days < 0:
            raise UserError(_("The trigger delay cannot be negative."))
        if self.min_interval_days < 1:
            raise UserError(_(
                "The minimum delay since last reminder "
                "must be strictly positive."))
        journal_object = self.env['account.journal']
        partner_object = self.env['res.partner']
        expense_sheet_object = self.env['hr.expense.sheet']
        aors_object = self.env['advance.overdue.reminder.step']
        user_id = self.env.user.id
        existing_actions = aors_object.search([
            ('user_id', '=', user_id), ('state', '=', 'draft')])
        existing_actions.unlink()
        purchase_journals = journal_object.search([
            ('company_id', '=', self.company_id.id),
            ('type', '=', 'purchase'),
            ])
        today = fields.Date.context_today(self)
        min_interval_date = today - relativedelta(days=self.min_interval_days)
        base_domain = self._prepare_base_domain()
        domain = self._prepare_remind_trigger_domain(base_domain)
        rg_res = expense_sheet_object.read_group(
            domain, ['address_id'], ['address_id'])
        action_ids = []
        for rg_re in rg_res:
            if rg_re['address_id']:
                partner_id = rg_re['address_id'][0]
            partner = partner_object.browse(partner_id)
            vals = self._prepare_reminder_step(
                partner, base_domain, min_interval_date, purchase_journals)
            if vals:
                action = aors_object.create(vals)
                action_ids.append(action.id)
        if not action_ids:
            raise UserError(_(
                "There are no overdue reminders."))
        xid = MOD + '.action_overdue_step_mass'
        action = self.env.ref(xid).read()[0]
        action['domain'] = [('id', 'in', action_ids)]
        return action


class HrAdvanceOverdueStartPayment(models.TransientModel):
    _name = 'hr.advance.overdue.start.payment'
    _inherit = 'overdue.reminder.start.payment'
    _description = 'Status of payments'

    advance_wizard_id = fields.Many2one(
        comodel_name='hr.advance.overdue.reminder.wizard',
        ondelete='cascade')
