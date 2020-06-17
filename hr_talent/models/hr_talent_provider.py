# Copyright 2020 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class HrTalentProvider(models.Model):
    _name = 'hr.talent.provider'
    _description = 'HR Talent Provider'

    active = fields.Boolean(
        default=True,
    )
    name = fields.Char(
        name='Name',
        required=True,
    )
    service = fields.Selection(
        selection=lambda self: self._selection_service(),
        required=True,
        readonly=True,
    )
    query_hint = fields.Html(
        string='Query Hint',
        compute='_compute_query_hint',
    )
    api_base = fields.Char()
    origin = fields.Char()
    username = fields.Char()
    password = fields.Char()
    key = fields.Binary()
    certificate = fields.Binary()
    passphrase = fields.Char()
    certificate_public_key = fields.Text()
    certificate_private_key = fields.Text()
    certificate_chain = fields.Text()
    company_id = fields.Many2one(
        string='Company',
        comodel_name='res.company',
        default=lambda self: self.env['res.company']._company_default_get(),
        ondelete='cascade',
    )

    @api.model
    def _get_available_services(self):
        """ Hook for extensions """
        return []

    @api.model
    def _selection_service(self):
        return self._get_available_services() + [('dummy', 'Dummy')]

    @api.model
    def values_service(self):
        return self._get_available_services()

    @api.multi
    def _compute_query_hint(self):
        """ Hook for extensions """
        for provider in self:
            provider.query_hint = False

    @api.multi
    def search(self, query):
        self.ensure_one()
        return self.env['hr.talent.provider.query'].create(
            self._get_query_values(query)
        )

    @api.multi
    def _search(self, query):
        """ Hook for extensions """
        self.ensure_one()
        # NOTE: This method should return ????
        return []

    @api.multi
    def _get_query_values(self, query):
        """ Hook for extensions """
        self.ensure_one()
        return {
            'provider_id': self.id,
            'query': query,
        }

    @api.multi
    def import_talent_values(self, url):
        """ Hook for extensions """
        # TODO: - extract data from page/url in form of values suitable for talent creation
        return None

    @api.multi
    def normalize_profile_url(self, url):
        """ Hook for extensions """
        self.ensure_one()
        return url

    @api.onchange('service')
    def onchange_service(self):
        if not self.name:
            self.name = list(filter(
                lambda service: service[0] == self.service,
                self._selection_service()
            ))[0][1]
