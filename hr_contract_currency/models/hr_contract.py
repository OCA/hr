# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrContract(models.Model):
    _inherit = 'hr.contract'

    currency_id = fields.Many2one(
        'res.currency',
        related=None,
        readonly=False,
        required=True,
        default=lambda self: self._get_default_currency_id(),
        track_visibility='onchange',
    )

    def _get_default_currency_id(self):
        return self.company_id.currency_id \
            or self.env.user.company_id.currency_id
