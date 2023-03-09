# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrStudy(models.Model):
    _name = "hr.study"
    _description = "Study"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    company_id = fields.Many2one(comodel_name="res.company")
