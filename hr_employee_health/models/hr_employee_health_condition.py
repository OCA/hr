# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeHealthCondition(models.Model):
    _name = 'hr.employee.health.condition'
    _description = 'HR Employee Health Condition'

    employee_id = fields.Many2one(
        string='Employee',
        comodel_name='hr.employee',
    )
    type_id = fields.Many2one(
        'hr.employee.health.condition.type',
        string='Condition',
        required=True,
    )
    severity_id = fields.Many2one(
        'hr.employee.health.condition.severity',
        string='Severity',
    )
    notes = fields.Text(
        string='Notes',
    )
