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
    color = fields.Integer(default=lambda self: self._get_default_color())

    _name_uniq = models.Constraint("UNIQUE(name)", "Tag name already exists !")
