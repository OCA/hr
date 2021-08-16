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

    common_department_with_user = fields.Boolean(
        compute='_common_department_with_user',
    )

    _defaults = {
        'common_department_with_user': False
    }

    @api.one
    @api.depends('employee_id.department_id', 'employee_id.department_ids')
    def _common_department_with_user(self):
        # This will check members in department_id field
        if any(employee in self.env.user.employee_ids.ids for employee in self.department_id.member_ids.ids):
            self.common_department_with_user = True
            return

        for department in self.employee_id.department_ids:
            # This will check members in department_ids relation
            if any(employee in self.env.user.employee_ids.ids for employee in department.members_ids.ids):
                self.common_department_with_user = True
                return

        self.common_department_with_user = False
