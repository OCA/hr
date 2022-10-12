# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    course_expiration_channel_id = fields.Many2one(
        related="company_id.course_expiration_channel_id", readonly=False
    )
    course_expiration_alerting_delay = fields.Integer(
        related="company_id.course_expiration_alerting_delay", readonly=False
    )
