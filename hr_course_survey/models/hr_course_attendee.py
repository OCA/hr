# Copyright 2021 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, fields, models, tools
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrCourseAttendee(models.Model):

    _inherit = "hr.course.attendee"

    survey_answer_id = fields.Many2one("survey.user_input", readonly=True)

    def _get_examination_survey_vals(self):
        vals = {}
        if self.employee_id.user_id:
            vals["user"] = self.employee_id.user_id
        else:
            vals["partner"] = (
                self.employee_id.address_id or self.employee_id.address_home_id
            )
        return vals

    def _notify_survey(self):
        template = self.env.ref("hr_course_survey.mail_template_user_input_invite")
        subject = (
            self.env["mail.template"]
            .with_context(safe=True)
            ._render_template(
                template.subject,
                "survey.user_input",
                self.survey_answer_id.id,
                post_process=True,
            )
        )
        body = self.env["mail.template"]._render_template(
            template.body_html,
            "survey.user_input",
            self.survey_answer_id.id,
            post_process=True,
        )
        # post the message
        mail_values = {
            "email_from": tools.formataddr((self.env.user.name, self.env.user.email)),
            "author_id": self.env.user.partner_id.id,
            "model": None,
            "res_id": None,
            "subject": subject,
            "body_html": body,
            "auto_delete": True,
        }
        if self.survey_answer_id.partner_id:
            mail_values["recipient_ids"] = [(4, self.survey_answer_id.partner_id.id)]
        else:
            mail_values["email_to"] = self.survey_answer_id.email
        return self.env["mail.mail"].sudo().create(mail_values)

    def _send_survey(self):
        vals = self._get_examination_survey_vals()
        survey = self.course_schedule_id.examination_survey_id
        self.survey_answer_id = survey._create_answer(**vals)
        self._notify_survey()

    def resend_survey(self):
        self.ensure_one()
        if self.survey_answer_id.state != "done":
            raise ValidationError(
                _(
                    "Survey cannot be sent because the "
                    "previous survey has not been answered"
                )
            )
        if self.result != "failed":
            raise ValidationError(_("Survey cannot be sent if the user has not failed"))
        self._send_survey()
        self.write({"result": "pending"})
