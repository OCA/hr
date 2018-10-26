# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeBloodType(models.Model):
    _name = 'hr.employee.blood.type'
    _description = 'HR Employee Blood Type'

    name = fields.Char(
        string='Type',
        required=True,
        translate=True
    )
