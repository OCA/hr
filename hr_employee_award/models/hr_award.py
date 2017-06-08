# -*- coding: utf-8 -*-
# © 2016 OpenSynergy Indonesia
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class HrAwardType(models.Model):
    _name = 'hr.award.type'
    _description = 'Employee Award Type'

    name = fields.Char(
        string='Award Type',
        required=True,
        translate=True,
        )
    code = fields.Char(
        string='Code',
        )
    type = fields.Selection(
        string='Type',
        selection=[
            ('internal', 'Internal'),
            ('external', 'External'),
        ],
        required=True,
        default='internal',
        )
    point = fields.Integer(
        string='Point',
        )
    active = fields.Boolean(
        string='Active',
        default=True,
        )


class HrAward(models.Model):
    _name = 'hr.award'
    _inherit = ['mail.thread']
    _decsription = 'Employee Award'

    @api.model
    def _default_company_id(self):
        return self.env.user.company_id.id

    name = fields.Char(
        string='# Award',
        required=True,
        readonly=True,
        default='/',
        )
    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
        required=True,
        readonly=True,
        states={
            'draft': [
                ('readonly', False),
                ],
            },
        )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        copy=False,
        default=_default_company_id,
    )
    award_type_id = fields.Many2one(
        string='Award Type',
        comodel_name='hr.award.type',
        required=True,
        readonly=True,
        states={
            'draft': [
                ('readonly', False),
                ],
            },
        )
    point = fields.Integer(
        string='Point',
        default=0,
        readonly=True,
        states={
            'draft': [
                ('readonly', False),
                ],
            },
        )
    date_issued = fields.Date(
        string='Date Issued',
        readonly=True,
        states={
            'approved': [
                ('readonly', False),
                ('required', True),
                ],
            },
        )
    note = fields.Text(
        string='Additional Description',
        )
    state = fields.Selection(
        string='State',
        selection=[
            ('draft', 'Draft'),
            ('confirmed', 'Waiting for Approval'),
            ('approved', 'Approved'),
            ('issued', 'Issued'),
            ('cancelled', 'Cancelled'),
            ],
        required=True,
        readonly=True,
        default='draft',
        )

    @api.multi
    def button_confirm(self):
        for award in self:
            award.write(self._prepare_confirm_data(award))

    @api.multi
    def button_approve(self):
        for award in self:
            award.write(self._prepare_approve_data(award))

    @api.multi
    def button_issue(self):
        for award in self:
            award.write(self._prepare_issue_data(award))

    @api.multi
    def button_cancel(self):
        for award in self:
            award.write(self._prepare_cancel_data(award))

    @api.multi
    def button_restart(self):
        for award in self:
            award.write(self._prepare_restart_data(award))

    @api.onchange('award_type_id')
    def onchange_award_type(self):
        if self.award_type_id:
            self.point = self.award_type_id.point
        else:
            self.point = 0

    @api.model
    def _prepare_confirm_data(self, award):
        self.ensure_one()
        return {
            'state': 'confirmed',
            }

    @api.model
    def _prepare_approve_data(self, award):
        self.ensure_one()
        return {
            'state': 'approved',
            }

    @api.model
    def _prepare_issue_data(self, award):
        self.ensure_one()
        if award.name == '/':
            name = self.env['ir.sequence'].get('hr.award')
        else:
            name = award.name
        return {
            'name': name,
            'state': 'issued',
            }

    @api.model
    def _prepare_cancel_data(self, award):
        self.ensure_one()
        return {
            'state': 'cancelled',
            }

    @api.model
    def _prepare_restart_data(self, award):
        self.ensure_one()
        return {
            'state': 'draft',
            }
