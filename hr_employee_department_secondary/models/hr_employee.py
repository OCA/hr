from odoo import api, exceptions, fields, models, _


class Employee(models.Model):
    _inherit = ['hr.employee']

    secondary_department_ids = fields.Many2many(
        'hr.department', 'employee_department_rel',
        'employee_id', 'department_id',
        domain="[('id', '!=', department_id)]",
        string='Secondary departments')

    @api.constrains('department_id', 'secondary_department_ids')
    def _check_departments(self):
        for employee in self:
            if employee.department_id in employee.secondary_department_ids:
                raise exceptions.ValidationError(
                    _('The main department must be different '
                      'from the secondary departments.'))

class Department(models.Model):
    _inherit = ['hr.department']

    members_ids = fields.Many2many(
        'hr.employee', 'employee_department_rel',
        'department_id', 'employee_id',
        string='Members')
