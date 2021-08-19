from odoo import fields, models


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
