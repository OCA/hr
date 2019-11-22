# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    allowed_radius = fields.Float(
        related='company_id.allowed_radius',
        string="Check-in/Check-out allowed range.", readonly=False)
