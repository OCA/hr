# Copyright 2023 SDi Digital Group (https://www.sdi.es/odoo-cloud)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Workspace(models.Model):
    _name = "maintenance.workspace"
    _inherit = "mail.thread"
    _description = "Workspace"

    name = fields.Char(
        string="Name",
        required=True,
    )
    description = fields.Char(
        string="Description",
    )
    location = fields.Char(
        string="Location",
    )
    equipment_ids = fields.One2many(
        comodel_name="maintenance.equipment",
        inverse_name="workspace_id",
    )
    equipment_count = fields.Integer(
        name="Equipments",
        compute="_compute_equipment_count",
        store=True,
    )
    employee_ids = fields.Many2many(
        comodel_name="hr.employee",
        string="Employees",
    )
    employee_count = fields.Integer(
        string="Employee count",
        compute="_compute_employee_count",
        store=True,
    )
    employee_equipment_count = fields.Integer(
        string="Employee Equipment Count",
        compute="_compute_employee_equipment_count",
        store=True,
    )

    @api.depends("equipment_ids")
    def _compute_equipment_count(self):
        for workspace in self:
            workspace.equipment_count = len(workspace.equipment_ids)

    @api.depends("employee_ids")
    def _compute_employee_count(self):
        for workspace in self:
            workspace.employee_count = len(workspace.employee_ids)

    @api.depends("employee_ids", "employee_ids.equipment_ids")
    def _compute_employee_equipment_count(self):
        for workspace in self:
            workspace_empl_equipment_count = 0
            if len(workspace.employee_ids) > 0:
                for employee in workspace.employee_ids:
                    equipment_count = len(employee.equipment_ids)
                    workspace_empl_equipment_count += equipment_count
            workspace.employee_equipment_count = workspace_empl_equipment_count

    def button_employee_equipment_count(self):
        return {
            "name": "Employee Equipments",
            "view_type": "form",
            "view_mode": "tree,form",
            "res_model": "maintenance.equipment",
            "type": "ir.actions.act_window",
            "domain": [("employee_id", "in", self.employee_ids.ids)],
        }
