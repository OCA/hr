# Copyright 2017 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models


class HrEmployeeIdentificationType(models.Model):
    _name = "hr.employee.identification.type"
    _description = "Identification/Passport"
    _order = "name"

    name = fields.Char(required=True)
