# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import UserError


class HrPersonalEquipment(models.Model):
    _inherit = "hr.personal.equipment"

    location_id = fields.Many2one(related="equipment_request_id.location_id")
    procurement_group_id = fields.Many2one(
        "stock.reference",
        "Stock Reference",
        readonly=True,
        help="Reference linking the stock moves to this equipment request.",
        related="equipment_request_id.procurement_group_id",
    )
    qty_delivered = fields.Float(
        "Delivered Quantity",
        copy=False,
        compute="_compute_qty_delivered",
        compute_sudo=True,
        store=True,
    )
    move_ids = fields.One2many(
        "stock.move", "personal_equipment_id", string="Stock Moves"
    )
    skip_procurement = fields.Boolean(compute="_compute_skip_procurement")

    @api.depends("state", "product_id", "product_id.type")
    def _compute_skip_procurement(self):
        for record in self:
            record.skip_procurement = record._skip_procurement()

    @api.depends(
        "move_ids.state",
        "move_ids.scrap_id",
        "move_ids.quantity",
        "move_ids.product_uom",
    )
    def _compute_qty_delivered(self):
        for line in self:
            qty = 0.0
            for move in line.move_ids.filtered(
                lambda r, line=line: r.state == "done"
                and not r.scrap_id
                and line.product_id == r.product_id
            ):
                qty += move.product_uom._compute_quantity(
                    move.quantity, line.product_uom_id
                )
            line.qty_delivered = qty

    def _skip_procurement(self):
        return self.product_id.type == "service"

    def _prepare_procurement_values(self):
        """Prepare specific key for moves or other components that
        will be created from a procurement rule
        coming from a stock request. This method could be override
        in order to add other custom key that could be used in
        move/po creation.
        """
        return {
            "reference_ids": self.procurement_group_id,
            "partner_id": self.employee_id.user_id.partner_id.id,
            "personal_equipment_id": self.id,
        }

    def _get_company(self):
        return self.employee_id.company_id or self.env.company

    def _action_launch_procurement_rule(self):
        """
        Run the stock rules for the equipment request allocations.
        """
        errors = []
        for allocation in self:
            if allocation.skip_procurement:
                continue

            values = allocation._prepare_procurement_values()
            try:
                # We launch with sudo because potentially we could create
                # objects that the user is not authorized to create, such
                # as PO.
                procurement = self.env["stock.rule"].Procurement(
                    allocation.product_id,
                    allocation.quantity,
                    allocation.product_uom_id,
                    allocation.location_id,
                    allocation.equipment_request_id.name,
                    allocation.equipment_request_id.name,
                    allocation._get_company(),
                    values,
                )
                self.env["stock.rule"].sudo().run([procurement])
            except UserError as error:
                errors.append(error.args[0])
        if errors:
            raise UserError("\n".join(errors))
        return True

    def _accept_request(self):
        res = super()._accept_request()
        self._action_launch_procurement_rule()
        return res

    def _validate_allocation_vals(self):
        res = super()._validate_allocation_vals()
        if self.skip_procurement:
            res["qty_delivered"] = self.quantity
        return res
