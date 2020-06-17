# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models, api


class HrTalentSourcingWizard(models.TransientModel):
    _name = 'hr.talent.sourcing.wizard'
    _description = 'HR Talent Sourcing Wizard'

    provider_id = fields.Many2one(
        string='Provider',
        comodel_name='hr.talent.provider',
        required=True,
    )
    query_hint = fields.Html(
        string='Query Hint',
        related='provider_id.query_hint',
    )
    query = fields.Char(
        string='Query',
        required=True,
    )

    @api.multi
    def _get_query_values(self):
        """ Hook for extensions """
        self.ensure_one()
        return {
            'provider_id': self.provider_id.id,
            'query': self.query,
        }

    @api.multi
    def _create_query(self):
        """ Hook for extensions """
        self.ensure_one()
        return self.env['hr.talent.provider.query'].create(
            self._get_query_values()
        )

    @api.multi
    def action_submit_query(self):
        self.ensure_one()
        query = self._create_query()
        query.enqueue()
        return {'type': 'ir.actions.act_window_close'}
