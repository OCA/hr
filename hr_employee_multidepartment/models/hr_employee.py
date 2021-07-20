# -*- coding: utf-8 -*-

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

    sharing_departments_with_employee = fields.Boolean(
        compute='_has_common_dep',
        store=True,
    )

    @api.depends('sharing_department_with_employee')
    def _has_common_dep(self):
        members = []
        for department in self.employee_id.department_ids:
            # This will add regular members in department_id
            members += department.member_ids.ids
            # This will add members in department_ids relation
            members += department.members_ids.ids
        self.sharing_departments_with_employee = self.env.uid in members

