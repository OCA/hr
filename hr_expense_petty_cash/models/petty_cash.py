# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class PettyCash(models.Model):
    _name = 'petty.cash'
    _description = 'Petty Cash'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Petty Cash Holder',
        domain=[('supplier', '=', True)],
        required=True,
    )
    account_id = fields.Many2one(
        comodel_name='account.account',
        string='Petty Cash Account',
        required=True,
    )
    petty_cash_limit = fields.Float(
        string='Max Limit',
        required=True,
    )
    petty_cash_balance = fields.Float(
        string='Balance',
        compute='_compute_petty_cash_balance',
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal',
    )
    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)',
         'Petty Cash Holder must be unique!'),
    ]

    @api.depends('partner_id', 'account_id')
    def _compute_petty_cash_balance(self):
        aml_env = self.env['account.move.line']
        for rec in self:
            aml = aml_env.search([('partner_id', '=', rec.partner_id.id),
                                  ('account_id', '=', rec.account_id.id)])
            balance = sum([line.debit - line.credit for line in aml])
            rec.petty_cash_balance = balance
