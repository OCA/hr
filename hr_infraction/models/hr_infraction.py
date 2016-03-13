# -*- coding: utf-8 -*-
# © 2013 Michael Telahun Makonnen <mmakonnen@gmail.com>
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HrInfractionCatagory(models.Model):
    _name = 'hr.infraction.category'
    _description = 'Infraction Type'

    name = fields.Char(
        string='Name',
        required=True,
        translate=True,
    )
    code = fields.Char(
        string='Code',
        required=True,
    )


class HrInfractionWarning(models.Model):
    _name = 'hr.infraction.warning'
    _description = 'Infraction Warning'

    name = fields.Char(
        string='Warning',
        required=True,
        translate=True,
        )

    code = fields.Char(
        string='Code',
        )

    category_ids = fields.Many2many(
        string='Infraction Category(s)',
        comodel_name='hr.infraction.category',
        relation='rel_inf_warn_categ',
        column1='warning_id',
        column2='category_id',
        )


class HrInfraction(models.Model):
    _name = 'hr.infraction'
    _description = 'Infraction'
    _inherit = ['mail.thread']

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    name = fields.Char(
        string='# Infraction',
        required=False,
        readonly=True,
        default='/',
        copy=False,
    )
    date = fields.Date(
        string='Date',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default=fields.Date.today(),
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    company_id = fields.Many2one(
        store=True,
        comodel_name='res.company',
        string='Company',
        copy=False,
        default=_default_company_id,
    )

    category_id = fields.Many2one(
        comodel_name='hr.infraction.category',
        string='Category',
        required=False,
        readonly=True,
        copy=False,
        states={
            'confirm': [('required', True), ('readonly', False)],
            'approve': [('required', True), ('readonly', False)],
            }
    )
    warning_id = fields.Many2one(
        comodel_name='hr.infraction.warning',
        string='Warning',
        copy=False,
        required=False,
        readonly=True,
        states={
            'confirm': [('required', True), ('readonly', False)],
            'approve': [('required', True), ('readonly', False)],
            }
    )
    memo = fields.Text(
        string='Description',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('approve', 'Approved'),
            ('valid', 'Valid'),
            ('cancel', 'Cancelled'),
        ],
        string='State',
        readonly=True,
        default='draft',
        copy=False,
    )

    @api.multi
    def button_confirm(self):
        for inv in self:
            update_data = {
                'state': 'confirm',
                }
            if inv.name == '/':
                update_data.update({
                    'name': self.env['ir.sequence'].get('hr.infraction'),
                    })
            self.update(update_data)

    @api.multi
    def button_approve(self):
        for inv in self:
            self.update({'state': 'approve'})

    @api.multi
    def button_valid(self):
        for inv in self:
            self.update({'state': 'valid'})

    @api.multi
    def button_cancel(self):
        for inv in self:
            self.update({'state': 'cancel'})

    @api.multi
    def button_set_to_draft(self):
        for inv in self:
            self.update({'state': 'draft'})
