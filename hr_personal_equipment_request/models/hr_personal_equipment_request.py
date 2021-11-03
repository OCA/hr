# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class HrPersonalEquipmentRequest(models.Model):

    _name = "hr.personal.equipment.request"
    _description = "This model allows to create a personal equipment request"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(compute="_compute_name")
    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
        required=True,
        default=lambda self: self._default_employee_id(),
    )
    line_ids = fields.One2many(
        string="Personal Equipment",
        comodel_name="hr.personal.equipment",
        inverse_name="equipment_request_id",
        copy=True,
    )
    allocations_count = fields.Integer(compute="_compute_allocation_count")

    state = fields.Selection(
        [("draft", "Draft"), ("accepted", "Accepted"), ("cancelled", "Cancelled")],
        default="draft",
        tracking=True,
    )

    observations = fields.Text()

    def _default_employee_id(self):
        return self.env.user.employee_ids[:1]

    @api.depends("employee_id")
    def _compute_name(self):
        for rec in self:
            rec.name = _("Personal Equipment Request by %s") % rec.employee_id.name

    def accept_request(self):
        for rec in self:
            rec.write(rec._accept_request_vals())
            rec.line_ids._accept_request()

    def _accept_request_vals(self):
        return {"state": "accepted"}

    def cancel_request(self):
        for rec in self:
            rec.state = "cancelled"
            rec.line_ids.update({"state": "cancelled"})

    def _compute_equipment_request_count(self):
        self.equipment_request_count = len(self.equipment_request_ids)

    def _compute_allocation_count(self):
        self.allocations_count = len(self.line_ids)

    def action_open_personal_equipment(self):
        self.ensure_one()
        return {
            "name": _("Allocations"),
            "type": "ir.actions.act_window",
            "res_model": "hr.personal.equipment",
            "view_mode": "tree,form",
            "domain": [("id", "in", self.line_ids.ids)],
        }
