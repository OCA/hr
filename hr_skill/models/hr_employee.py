# Copyright 2013 Savoir-faire Linux
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    skill_ids = fields.Many2many(
        comodel_name='hr.skill',
        relation='skill_employee_rel',
        column1='employee_id',
        column2='skill_id',
        string='Skills',
        domain="[('child_ids', '=', False)]",
    )
