# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _


class WizardTheoreticalTime(models.TransientModel):

    _name = 'wizard.theoretical.time'
    _description = 'Filtered Theoretical Time'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    department_id = fields.Many2one(
        'hr.department', string='Department'
    )
    category_ids = fields.Many2many(
        'hr.employee.category', string='Tag'
    )

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        if self.env.user.employee_ids:
            res[
                'department_id'
            ] = self.env.user.employee_ids[0].department_id.id
        return res

    def _prepare_employee_domain(self):
        res = []
        if self.category_ids:
            res.append(('category_ids', 'in', self.category_ids.ids))
        if self.department_id:
            res.append(('department_id', 'child_of', self.department_id.id))
        return res

    @api.multi
    def populate(self):
        domain = self._prepare_employee_domain()
        self.employee_ids = self.env['hr.employee'].search(domain)
        action = {
            'name': _('Select Employees to Analyze Theoretical Time'),
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.theoretical.time',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context,
        }
        return action

    @api.multi
    def view_report(self):
        self.ensure_one()
        action = {
            'type': 'ir.actions.act_window',
            'name': 'Theoretical vs Attended Time Analysis',
            'res_model': 'hr.attendance.theoretical.time.report',
            'domain': [('employee_id', 'in', self.employee_ids.ids)],
            'view_mode': 'pivot,graph',
        }
        return action
