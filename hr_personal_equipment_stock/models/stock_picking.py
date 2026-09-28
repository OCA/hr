# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    equipment_request_id = fields.Many2one(
        "hr.personal.equipment.request",
        compute="_compute_equipment_request_id",
        store=True,
    )

    @api.depends("move_ids.personal_equipment_id.equipment_request_id")
    def _compute_equipment_request_id(self):
        for picking in self:
            picking.equipment_request_id = (
                picking.move_ids.personal_equipment_id.equipment_request_id[:1]
            )

    def _action_done(self):
        res = super()._action_done()
        for picking in self:
            if picking.equipment_request_id:
                for move in picking.move_ids:
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
