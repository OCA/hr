# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class EmployeeSkill(models.Model):
    _name = 'hr.employee.skill'

    employee_id = fields.Many2one('hr.employee', string="Employee")

    skill_id = fields.Many2one('hr.skill', string="Skill")
    level = fields.Selection([('0', 'Junior'),
                              ('1', 'Intermediate'),
                              ('2', 'Senior'),
                              ('3', 'Expert')], 'Level')

    _sql_constraints = [
        ('hr_employee_skill_uniq', 'unique(employee_id, skill_id)',
         "This employee already has that skill!"),
    ]
