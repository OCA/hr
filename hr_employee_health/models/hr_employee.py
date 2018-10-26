# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    health_condition_ids = fields.One2many(
        string='Health Conditions',
        comodel_name='hr.employee.health.condition',
        inverse_name='employee_id',
        groups='hr.group_hr_user',
    )
    blood_type = fields.Many2one(
        string='Blood Type',
        comodel_name='hr.employee.blood.type',
        groups='hr.group_hr_user',
    )
    health_notes = fields.Text(
        string='Health Notes',
        groups='hr.group_hr_user',
    )
