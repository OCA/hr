# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrCourseSchedule(models.Model):

    _inherit = "hr.course.schedule"

    examination_survey_id = fields.Many2one(
        "survey.survey", related="course_id.examination_survey_id",
    )

    def inprogress2validation(self):
        result = super().inprogress2validation()
        for record in self:
            if record.examination_survey_id:
                for attendee in record.course_attendee_ids:
                    attendee._send_survey()
        return result
