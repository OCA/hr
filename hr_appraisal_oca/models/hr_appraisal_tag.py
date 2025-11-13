# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from random import randint

from odoo import fields, models


class HrAppraisalTag(models.Model):
    _name = "hr.appraisal.tag"
    _description = "Appraisal Tags"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char("Tag Name", required=True)
    color = fields.Integer(default=_get_default_color)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Tag name already exists !"),
    ]
