import logging

from odoo import api, fields, models, _
from odoo.exceptions import UserError

class HrAppraisalEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"
    _description = "Basic Employee"

    last_appraisal_id = fields.Many2one('hr.appraisal.employee')

    def action_open_last_appraisal(self):
        self.ensure_one()
        last_appraisal = self._get_last_appraisal_id()
        if self.ongoing_appraisal_count > 1:
            return {
                    'name': _('New and Pending Appraisals'),
                    'type': 'ir.actions.act_window',
                    'view_mode': 'tree,form',
                    'res_model': 'hr.appraisal.employee',
                    'domain': [
                        ('employee_id', '=', self.id),
                        ('state', '!=', '3_done')
                    ],
                    'context': dict(self.env.context, default_employee_id=self.id),
                }
        else:
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.appraisal.employee',
                'res_id': last_appraisal.id,
                'context': self.env.context,
            }

    def _get_last_appraisal_id(self):
        state_priority = {'1_new': 0, '2_pending': 1, '3_done': 2}
        for employee in self:
            if employee.appraisal_ids:

                valid_appraisals = employee.appraisal_ids

                if len(valid_appraisals) == 1:
                    return valid_appraisals[0]
                elif len(valid_appraisals) == 0:
                    return False
                else:
                    # Sort by status and date
                    sorted_appraisals = valid_appraisals.sorted(
                    key=lambda r: (state_priority[r.state], r.date_close), reverse=True)

                    # Filter out appraisals that are not in 'done' status
                    non_done_appraisals = sorted_appraisals.filtered(lambda r: r.state != '3_done')

                    return non_done_appraisals[0] if non_done_appraisals else sorted_appraisals[0]
            else:
                return False

class HrAppraisalEmployee(models.Model):
    _inherit = 'hr.employee'

    appraisal_count = fields.Integer(string="Appraisal Count", compute='_compute_appraisal_count', store=True, groups="hr.group_hr_user")
    appraisal_ids = fields.One2many('hr.appraisal.employee', 'employee_id', string='Appraisal')
    last_appraisal_state = fields.Selection(related='last_appraisal_id.state', string='Status', readonly=True)
    ongoing_appraisal_count = fields.Integer(string="Ongoing Appraisal Count", compute='_compute_ongoing_appraisal_count', store=True, groups="hr.group_hr_user")
    allowed_user_ids = fields.Many2many('res.users', relation='hr_employee_manager_user_rel', column1='employee_id', column2='user_id', string='Allowed Users', compute='_compute_allowed_user_ids', store=True)

    @api.depends('parent_id')
    def _compute_allowed_user_ids(self):
        for employee in self:
            allowed_users = set()
            visited = set()
            current = employee.parent_id

            while current and current.id not in visited:
                visited.add(current.id)
                if current.user_id:
                    allowed_users.add(current.user_id.id)
                current = current.parent_id

            employee.allowed_user_ids = [(6, 0, list(allowed_users))]

    @api.depends('appraisal_ids')
    def _compute_appraisal_count(self):
        for employee in self:
            employee.appraisal_count = len(employee.appraisal_ids)

    @api.depends('appraisal_ids.state')
    def _compute_ongoing_appraisal_count(self):
        for employee in self:
            employee.ongoing_appraisal_count = len(employee.appraisal_ids.filtered(lambda a: a.state in ['1_new', '2_pending']))

class HrAppraisalEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    last_appraisal_id = fields.Many2one('hr.appraisal.employee', readonly=True)
