# Copyright 2020 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, _, api, tools
from odoo.exceptions import UserError

MOD = 'hr_expense_advance_overdue_reminder'


class AdvanceOverdueReminderStep(models.Model):
    _name = 'advance.overdue.reminder.step'
    _inherit = 'overdue.reminder.step'
    _transient = False
    _description = 'Expense Advance Overdue Reminder Step'
    _order = 'name desc'

    name = fields.Char(required=True, default='/', readonly=True, copy=False)
    partner_id = fields.Many2one(
        readonly=True, states={'draft': [('readonly', False)]})
    reminder_type = fields.Selection(
        readonly=True, states={'draft': [('readonly', False)]})
    mail_subject = fields.Char(
        readonly=True, states={'draft': [('readonly', False)]})
    mail_body = fields.Html(
        readonly=True, states={'draft': [('readonly', False)]})
    expense_sheet_ids = fields.Many2many(
        comodel_name='hr.expense.sheet',
        string='Overdue Expense Advance Sheet',
        readonly=True,
        states={'draft': [('readonly', False)]})

    def validate_mail(self):
        self.ensure_one()
        if not self.partner_id.email:
            raise UserError(_("E-mail missing on partner '%s'.")
                            % self.partner_id.display_name)
        if not self.mail_subject:
            raise UserError(_('Mail subject is empty.'))
        if not self.mail_body:
            raise UserError(_('Mail body is empty.'))
        xmlid = MOD + '.overdue_advance_reminder_mail_template'
        mvals = self.env.ref(xmlid).generate_email(self.id)
        mvals.update({
            'subject': self.mail_subject,
            'body_html': self.mail_body,
            })
        mvals.pop('attachment_ids', None)
        mvals.pop('attachments', None)
        mail = self.env['mail.mail'].create(mvals)
        vals = {'mail_id': mail.id}
        return vals

    def _prepare_overdue_reminder_action(self, vals):
        vals.update({
            'user_id': self.user_id.id,
            'reminder_type': self.reminder_type,
            'reminder_ids': [],
            'company_id': self.company_id.id,
            'commercial_partner_id': self.commercial_partner_id.id,
            'partner_id': self.partner_id.id,
            })
        for exp in self.expense_sheet_ids:
            rvals = {'expense_sheet_id': exp.id}
            if self.reminder_type != 'phone':
                rvals['counter'] = exp.overdue_reminder_counter + 1
            vals['reminder_ids'].append((0, 0, rvals))

    def print_expense_advance(self):
        raise UserError(_('Not Found Advance Overdue Letter.'))

    def validate(self):
        aora_object = self.env['advance.overdue.reminder.action']
        ma_object = self.env['mail.activity']
        sequence_object = self.env['ir.sequence']
        self.check_warnings()
        for rec in self:
            vals = {}
            if rec.reminder_type == 'mail':
                vals = rec.validate_mail()
            elif rec.reminder_type == 'phone':
                vals = rec.validate_phone()
            elif rec.reminder_type == 'post':
                vals = rec.validate_post()
            rec._prepare_overdue_reminder_action(vals)
            aora_object.create(vals)
            if rec.create_activity:
                ma_object.create(self._prepare_mail_activity())
            sequence_code = 'advance.overdue.reminder.step'
            rec.name = sequence_object.with_context(
                ir_sequence_date=rec.date).next_by_code(sequence_code)
        self.write({'state': 'done'})
        return True

    def skip(self):
        return self.write({'state': 'skipped'})

    def total_residual(self):
        self.ensure_one()
        res = {}
        for exp in self.expense_sheet_ids:
            if exp.currency_id in res:
                res[exp.currency_id] += exp.residual
            else:
                res[exp.currency_id] = exp.residual
        return res.items()

    @api.multi
    def _create_mail_template(self, vals):
        self.ensure_one()
        commercial_partner = self.env['res.partner'].browse(
            vals['commercial_partner_id'])
        xmlid = MOD + '.overdue_advance_reminder_mail_template'
        mail_tpl = self.env.ref(xmlid)
        mail_tpl_lang = mail_tpl.with_context(
            lang=commercial_partner.lang or 'en_US')
        mail_subject = mail_tpl_lang._render_template(
            mail_tpl_lang.subject, self._name, self.id)
        mail_body = mail_tpl_lang._render_template(
            mail_tpl_lang.body_html, self._name, self.id)
        if mail_tpl.user_signature:
            signature = self.env.user.signature
            if signature:
                mail_body = tools.append_content_to_html(
                    mail_body, signature, plaintext=False)
        mail_body = tools.html_sanitize(mail_body)
        self.write({
            'mail_subject': mail_subject,
            'mail_body': mail_body,
            })
        return self

    @api.model
    def create(self, vals):
        res = super().create(vals)
        return res._create_mail_template(vals)

    @api.constrains('expense_sheet_ids')
    def _check_expense_sheet_ids(self):
        vals = {'commercial_partner_id': self.commercial_partner_id.id}
        return self._create_mail_template(vals)
