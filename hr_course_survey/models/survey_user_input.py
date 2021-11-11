# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SurveyUserInput(models.Model):

    _inherit = "survey.user_input"

    hr_course_attendee_ids = fields.One2many(
        "hr.course.attendee", inverse_name="survey_answer_id"
    )

    def _attendee_write_vals(self):
        return {
            "result": "failed"
            if not self.quizz_passed and self.survey_id.scoring_type != "no_scoring"
            else "passed"
        }

    def _mark_done(self):
        result = super()._mark_done()
        for user_input in self:
            if user_input.hr_course_attendee_ids:
                user_input.hr_course_attendee_ids.write(
                    user_input._attendee_write_vals()
                )
        return result
