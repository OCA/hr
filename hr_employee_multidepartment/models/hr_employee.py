from odoo import api, fields, models


class Employee(models.Model):
    _inherit = ['hr.employee']

    department_ids = fields.Many2many(
        'hr.department', 'employee_department_rel',
        'employee_id', 'department_id',
        string='Departments')

class Department(models.Model):
    _inherit = ['hr.department']

    members_ids = fields.Many2many(
        'hr.employee', 'employee_department_rel',
        'department_id', 'employee_id',
        string='Members')

class HrLeave(models.Model):
    _inherit = ['hr.leave']

    common_department_with_user = fields.Boolean(
        compute='_compute_common_department_with_user',
        default=False,
    )

    @api.depends('employee_id.department_id', 'employee_id.department_ids')
    def _compute_common_department_with_user(self):
        for record in self:
            # This will check members in department_id field
            if any(employee in record.env.user.employee_ids.ids for employee in record.department_id.member_ids.ids):
                record.common_department_with_user = True
                return

            for department in record.employee_id.department_ids:
                # This will check members in department_ids relation
                if any(employee in record.env.user.employee_ids.ids for employee in department.members_ids.ids):
                    record.common_department_with_user = True
                    return

            record.common_department_with_user = False
