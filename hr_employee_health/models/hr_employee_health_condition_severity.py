# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeHealthConditionSeverity(models.Model):
    _name = 'hr.employee.health.condition.severity'
    _description = 'HR Employee Health Condition Severity'

    name = fields.Char(
        string='Severity',
        required=True,
        translate=True
    )
