# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class HrCourseSchedule(models.Model):
    _name = "hr.course.schedule"
    _description = "Course Schedule"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
    course_id = fields.Many2one("hr.course", string="Course", required=True)
    validity_end_date = fields.Date()
    start_date = fields.Date(
        string="Start date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    end_date = fields.Date(
        string="End date",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.user.company_id.currency_id,
    )
    cost = fields.Monetary(string="Course Cost", required=True, tracking=True)
    authorized_by = fields.Many2one(
        string="Authorized by",
        comodel_name="hr.employee",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("waiting_attendees", "Waiting attendees"),
            ("in_progress", "In progress"),
            ("in_validation", "In validation"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        required=True,
        readonly=True,
        default="draft",
        tracking=True,
    )

    comment = fields.Text("Comment")
    training_company_id = fields.Many2one("res.partner", string="Training company")
    instructor_ids = fields.Many2many("res.partner", string="Instructor")
    place = fields.Char("Place")

    attendant_ids = fields.Many2many(
        "hr.employee",
        readonly=True,
        states={"waiting_attendees": [("readonly", False)]},
    )
    course_attendee_ids = fields.One2many(
        "hr.course.attendee",
        inverse_name="course_schedule_id",
        readonly=True,
        states={"in_validation": [("readonly", False)]},
    )

    course_expiration_alert_sent = fields.Boolean()

    @api.model
    def send_course_expiration_notification_email(self):
        company_id = self.env.context.get("company_id") or self.env.company.id
        channel = (
            self.env["res.company"].browse(company_id).course_expiration_channel_id
        )

        if not channel:
            _logger.info("no channel found for course expiration alerts")
            return False

        email_template = self.env.ref(
            "hr_course.mail_template_validity_reminder"
        ).with_context(lang=self.env.company.partner_id.lang)
        email_values = email_template.generate_email(self.ids, ["body_html", "subject"])

        values = email_values[self.id]
        self.with_context(email_from=channel.alias_id.display_name,).message_post(
            body=values["body_html"],
            channel_ids=channel.ids,
            message_type="email",
            subject=values["subject"],
        )
        return True

    @api.model
    def process_validity(self):
        company_id = self.env.context.get("company_id") or self.env.company.id
        course_expiration_alerting_delay = (
            self.env["res.company"].browse(company_id).course_expiration_alerting_delay
        )

        for course_schedule in self:
            if course_schedule.validity_end_date:
                if (
                    course_schedule.validity_end_date
                    - timedelta(days=course_expiration_alerting_delay)
                    <= fields.Date.today()
                ):
                    course_schedule.course_expiration_alert_sent = True
                    course_schedule.send_course_expiration_notification_email()

    def _cron_check_validity_date(self):
        items = self.search([("course_expiration_alert_sent", "=", False)])
        items.process_validity()

    @api.constrains("start_date", "end_date")
    def _check_start_end_dates(self):
        self.ensure_one()
        if self.start_date and self.end_date and (self.start_date > self.end_date):
            raise ValidationError(
                _("The start date cannot be later than the end date.")
            )

    def all_passed(self):
        for attendee in self.course_attendee_ids:
            attendee.result = "passed"

    def _draft2waiting_values(self):
        return {"state": "waiting_attendees"}

    def _attendee_values(self, attendee):
        return {"employee_id": attendee.id, "course_schedule_id": self.id}

    def _waiting2inprogress_values(self):
        attendants = []
        employee_attendants = self.course_attendee_ids.mapped("employee_id")
        for attendee in self.attendant_ids.filtered(
            lambda r: r not in employee_attendants
        ):
            attendants.append((0, 0, self._attendee_values(attendee)))
        deleted_attendees = ""
        for course_attendee in self.course_attendee_ids.filtered(
            lambda r: r.employee_id not in self.attendant_ids
        ):
            attendants += course_attendee._remove_from_course()
            deleted_attendees += "- %s <br></br>" % course_attendee.employee_id.name
        if deleted_attendees != "":
            message = (
                _("Employees removed from this course: <br></br>%s") % deleted_attendees
            )
            self.message_post(body=message)
        return {"state": "in_progress", "course_attendee_ids": attendants}

    def _inprogress2validation_values(self):
        return {"state": "in_validation"}

    def _validation2complete_values(self):
        return {"state": "completed"}

    def _back2draft_values(self):
        return {"state": "draft"}

    def _cancel_course_values(self):
        return {"state": "cancelled"}

    def draft2waiting(self):
        for record in self:
            record.write(record._draft2waiting_values())

    def waiting2inprogress(self):
        for record in self:
            record.write(record._waiting2inprogress_values())

    def inprogress2validation(self):
        for record in self:
            record.write(record._inprogress2validation_values())

    def validation2complete(self):
        for record in self:
            if self.course_attendee_ids.filtered(
                lambda r: r.result == "pending" and r.active
            ):
                raise ValidationError(
                    _("You cannot complete the course with pending results")
                )
            else:
                record.write(record._validation2complete_values())

    def back2draft(self):
        for record in self:
            record.write(record._back2draft_values())

    def cancel_course(self):
        for record in self:
            record.write(record._cancel_course_values())
