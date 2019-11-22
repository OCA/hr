# Copyright 2019 Eficent Business and IT Consulting Services S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class company(models.Model):
    _inherit = 'res.company'

    allowed_radius = fields.Float(
        'Allowed Radius (km)', default=0.0,
        help="Check-in/Check-out allowed range. 0 means no restrictions")
