# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_skill_ids = fields.One2many('hr.employee.skill',
                                         'employee_id',
                                         string="Employee Skill")
