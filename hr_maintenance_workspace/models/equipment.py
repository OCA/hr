# Copyright 2023 SDi Digital Group (https://www.sdi.es/odoo-cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    workspace_id = fields.Many2one(
        comodel_name="maintenance.workspace",
        string="Workspace",
        tracking=True,
    )
    equipment_assign_to = fields.Selection(
        selection_add=[("workspace", "Workspace"), ("other", "Other")],
        ondelete={
            "workspace": "set default",
            "other": "set default",
        },
    )

    @api.depends("equipment_assign_to")
    def _compute_equipment_assign(self):
        super()._compute_equipment_assign()
        for equipment in self:
            if equipment.equipment_assign_to in ["employee", "department"]:
                equipment.workspace_id = False
            elif equipment.equipment_assign_to == "workspace":
                equipment.workspace_id = equipment.workspace_id
                equipment.department_id = False
                equipment.employee_id = False
            else:
                equipment.workspace_id = equipment.workspace_id
