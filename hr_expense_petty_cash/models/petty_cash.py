# Copyright 2019 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields


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
        domain=[('internal_group', '=', 'asset')],
        required=True,
    )
    petty_cash_limit = fields.Float(
        string='Max Limit',
        default=0.0,
        required=True,
    )
    petty_cash_balance = fields.Float(
        string='Balance',
        compute='_compute_petty_cash_balance',
    )
    _sql_constraints = [
        ('partner_uniq', 'unique(partner_id)',
         'Petty Cash Holder must be unique!'),
    ]

    @api.multi
    def _compute_petty_cash_balance(self):
        move = self.env['account.move.line']
        for rec in self:
            moves = move.search([('partner_id', '=', rec.partner_id.id),
                                 ('account_id', '=', rec.account_id.id)])
            balance = sum([line.debit - line.credit for line in moves])
            rec.petty_cash_balance = balance
