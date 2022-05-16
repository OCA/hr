###############################################################################
# For copyright and license notices, see __manifest__.py file in root directory
###############################################################################
from odoo import api, fields, models


class Workspace(models.Model):
    _name = 'workspace.workspace'
    _inherit = 'mail.thread'
    _description = 'Workspace'

    item_ids = fields.One2many(
        comodel_name='workspace.item',
        inverse_name='workspace_id',
        string='Items',
    )
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        relation='employee_workspace_rel',
        column1='workspace_id',
        column2='employee_id',
        string='Employees',
    )
    workspace_id = fields.Many2one(
        comodel_name='workspace.workspace',
        string='Workspace',
    )
    workspace_ids = fields.One2many(
        comodel_name='workspace.workspace',
        inverse_name='workspace_id',
        string='Workspaces',
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    description = fields.Char(
        string='Description',
    )
    location = fields.Char(
        string='Location',
    )
    item_count = fields.Integer(
        string="Item Count",
        compute='_compute_item_count',
    )
    employee_count = fields.Integer(
        string='Employee Count',
        compute='_compute_employee_count',
    )
    internal_item_count = fields.Integer(
        string='Internal Item Count',
        compute='_compute_internal_item_count',
    )
    employee_item_count = fields.Integer(
        string='Employee Item Count',
        compute='_compute_employee_item_count',
    )

    def _compute_item_count(self):
        for rec in self:
            rec.item_count = len(rec.item_ids)

    def _compute_employee_count(self):
        for rec in self:
            rec.employee_count = self.env['hr.employee'].search(
                [('workspace_ids', 'like', rec.id)],
                count=True,
            )

    def _internal_workspaces(self):
        internal_workspaces = self.workspace_ids
        if len(self.workspace_ids) > 0:
            for workspace in self.workspace_ids:
                internal_workspaces += workspace._internal_workspaces()
        return internal_workspaces

    @api.depends('workspace_ids')
    def _compute_internal_item_count(self):
        for rec in self:
            rec.internal_item_count = 0
            if rec._internal_workspaces():
                for workspace in rec._internal_workspaces():
                    for item in workspace.item_ids:
                        rec.internal_item_count += 1

    def button_internal_item_count(self):
        workspaces = self._internal_workspaces()
        return{
            'name': 'Internal Items',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'workspace.item',
            'type': 'ir.actions.act_window',
            'domain': [('workspace_id', 'in', workspaces.ids)],
        }

    @api.depends('employee_ids')
    def _compute_employee_item_count(self):
        for rec in self:
            rec.employee_item_count = 0
            if len(rec.employee_ids) > 0:
                for employee in rec.employee_ids:
                    for item in employee.item_ids:
                        rec.employee_item_count += 1

    def button_employee_item_count(self):
        return{
            'name': 'Employee Items',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'workspace.item',
            'type': 'ir.actions.act_window',
            'domain': [('employee_id', 'in', self.employee_ids.ids)],
        }

    @api.onchange('workspace_id')
    def _onchange_workspace_id(self):
        if self.workspace_id:
            self.location = self.workspace_id.location
