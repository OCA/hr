# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"
    personal_equipment_id = fields.Many2one(
        "hr.personal.equipment", "Employee Personal Equipment"
    )

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super()._prepare_merge_moves_distinct_fields()
        distinct_fields.append("personal_equipment_id")
        return distinct_fields

    def _action_cancel(self):
        res = super()._action_cancel()
        for rec in self.sudo():
            if not rec.personal_equipment_id.qty_delivered:
                rec.personal_equipment_id.update({"state": "cancelled"})
            else:
                rec.personal_equipment_id.update({"state": "valid"})
        return res
