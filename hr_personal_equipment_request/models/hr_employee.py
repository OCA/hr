# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    equipment_request_ids = fields.One2many(
        comodel_name="hr.personal.equipment.request",
        inverse_name="employee_id",
    )

    personal_equipment_ids = fields.One2many(
        comodel_name="hr.personal.equipment",
        inverse_name="employee_id",
        domain=[("state", "not in", ["draft", "cancelled"])],
    )

    equipment_request_count = fields.Integer(
        compute="_compute_equipment_request_count",
    )

    personal_equipment_count = fields.Integer(
        compute="_compute_personal_equipment_count"
    )

    def _compute_equipment_request_count(self):
        self.equipment_request_count = len(self.equipment_request_ids)

    def _compute_personal_equipment_count(self):
        self.personal_equipment_count = len(self.personal_equipment_ids)

    def action_open_equipment_request(self):
        self.ensure_one()
        return {
            "name": _("Equipment Request"),
            "type": "ir.actions.act_window",
            "res_model": "hr.personal.equipment.request",
            "view_mode": "tree,form",
            "context": {"group_by": "state"},
            "domain": [("id", "in", self.equipment_request_ids.ids)],
        }

    def action_open_personal_equipment(self):
        self.ensure_one()
        return {
            "name": _("Personal Equipment"),
            "type": "ir.actions.act_window",
            "res_model": "hr.personal.equipment",
            "context": {"group_by": "state"},
            "view_mode": "tree,form",
            "domain": [("id", "in", self.personal_equipment_ids.ids)],
        }
