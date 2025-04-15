# Copyright 2025 Open SOurce Integrators
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class HrShiftPosition(models.Model):
    _name = "hr.shift.position"
    _description = "Shift Position"

    name = fields.Char(required=True, translate=True)
