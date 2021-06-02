# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools.translate import _
import datetime


class Employee(models.Model):
    _inherit = ['hr.employee']

    department_ids = fields.Many2many(
        'hr.department', 'employee_department_rel',
        'employee_id', 'department_id',
        string='Departments')

    @api.onchange('department_ids')
    def _add_member_department(self):
        old_dept_ids = self._origin.department_ids.ids + self._origin.department_id.ids
        new_dept_ids = self.department_ids.ids
        add_member = set(new_dept_ids) - set(old_dept_ids)
        remove_member = set(old_dept_ids) - set(new_dept_ids)
        #import pudb;pu.db
        employee_id = self._origin.id
        if add_member:
            d = self.env['hr.department'].browse(add_member)
            d.write({'member_ids': [(4, employee_id)]})
        if remove_member:
            d = self.env['hr.department'].browse(remove_member)
            d.write({'member_ids': [(3, employee_id)]})


class Department(models.Model):
    _inherit = ['hr.department']

    members_ids = fields.Many2many(
        'hr.employee', 'department_member_rel',
        'department_ids', 'member_id',
        string='Members')
