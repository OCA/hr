# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.fields import Date


class HrPersonalEquipment(models.Model):

    _name = "hr.personal.equipment"
    _description = "Adds personal equipment information and allocation"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name")
    product_id = fields.Many2one(
        comodel_name="product.product",
        required=True,
        domain=[("is_personal_equipment", "=", True)],
    )
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        related="equipment_request_id.employee_id",
        store=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("accepted", "Accepted"),
            ("valid", "Valid"),
            ("expired", "Expired"),
            ("cancelled", "Cancelled"),
        ],
        default="draft",
        tracking=True,
    )
    start_date = fields.Date()
    expiry_date = fields.Date()
    equipment_request_id = fields.Many2one(
        comodel_name="hr.personal.equipment.request", required=True, ondelete="cascade"
    )
    quantity = fields.Integer(default=1)
    product_uom_id = fields.Many2one("uom.uom", "Unit of Measure")

    @api.onchange("product_id")
    def _onchange_uom_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id
        return {
            "domain": {
                "product_uom_id": [
                    ("category_id", "=", self.product_uom_id.category_id.id)
                ]
            }
        }

    @api.depends("product_id", "employee_id")
    def _compute_name(self):
        for rec in self:
            if rec.product_id.name and rec.employee_id.name:
                rec.name = "{} to {}".format(rec.product_id.name, rec.employee_id.name)
            else:
                rec.name = False

    def _validate_allocation_vals(self):
        return {
            "state": "valid",
            "start_date": fields.Date.context_today(self)
            if not self.start_date
            else self.start_date,
        }

    def validate_allocation(self):
        for rec in self:
            rec.write(rec._validate_allocation_vals())

    def expire_allocation(self):
        for rec in self:
            rec.state = "expired"
            if not rec.expiry_date:
                rec.expiry_date = Date.today()

    def _accept_request_vals(self):
        return {"state": "accepted"}

    def _accept_request(self):
        for rec in self:
            rec.write(rec._accept_request_vals())
