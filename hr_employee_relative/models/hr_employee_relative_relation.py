# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeRelativeRelation(models.Model):
    _name = "hr.employee.relative.relation"
    _description = "HR Employee Relative Relation"

    name = fields.Char(string="Relation", required=True, translate=True)
