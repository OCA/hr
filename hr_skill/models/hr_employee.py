# Copyright 2013 Savoir-faire Linux
# Copyright 2018-2019 Brainbean Apps
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    employee_skill_ids = fields.One2many(
        string='Skills',
        comodel_name='hr.employee.skill',
        inverse_name='employee_id',
    )
