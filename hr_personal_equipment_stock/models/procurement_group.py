# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProcurementGroup(models.Model):

    _inherit = "procurement.group"

    equipment_request_id = fields.Many2one("hr.personal.equipment.request")
