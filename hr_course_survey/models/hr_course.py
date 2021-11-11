# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrCourse(models.Model):

    _inherit = "hr.course"

    examination_survey_id = fields.Many2one(
        "survey.survey",
        domain=[("state", "=", "open"), ("scoring_type", "!=", "no_scoring")],
    )
