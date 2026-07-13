# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    equipment_request_id = fields.Many2one(
        related="group_id.equipment_request_id", store=True
    )

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            if picking.equipment_request_id:
                for move in picking.move_ids_without_package:
                    if move.state == "done":
                        request_lines = (
                            picking.equipment_request_id.sudo().line_ids.filtered(
                                lambda x, move=move: x.product_id == move.product_id
                            )
                        )
                        for line in request_lines:
                            if line.qty_delivered:
                                if line.quantity <= line.qty_delivered:
                                    line.validate_allocation()
        return res
