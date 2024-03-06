# Copyright 2023 SDi Digital Group (https://www.sdi.es/odoo-cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    workspace_ids = fields.Many2many(
        comodel_name="maintenance.workspace",
        string="Workspaces",
    )
    workspace_count = fields.Integer(
        name="Workspaces",
        compute="_compute_workspace_count",
    )

    @api.depends("workspace_ids")
    def _compute_workspace_count(self):
        for employee in self:
            employee.workspace_count = len(employee.workspace_ids)

    def button_employee_workspaces(self):
        return {
            "name": _("Workspaces"),
            "view_mode": "tree,form",
            "res_model": "maintenance.workspace",
            "type": "ir.actions.act_window",
            "domain": [("employee_ids", "=", self.id)],
        }
