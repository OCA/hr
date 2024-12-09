# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockLocation(models.Model):

    _inherit = "stock.location"

    is_personal_equipment_location = fields.Boolean(
        string="Is personal equipment location?"
    )
    # This field is used for filter purpose in the
    # hr.personal.equipment.request location field
