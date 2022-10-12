# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HRCourseAttendee(models.Model):
    _name = "hr.course.attendee"
    _description = "Course Attendee"

    course_schedule_id = fields.Many2one(
        "hr.course.schedule", ondelete="cascade", readonly=True, required=True
    )
    course_id = fields.Many2one(related="course_schedule_id.course_id")
    course_validity_end_date = fields.Date(
        related="course_schedule_id.validity_end_date"
    )

    name = fields.Char(related="course_schedule_id.name", readonly=True)
    course_expiration_alert_sent = fields.Boolean(
        help="Shows if notification email for course was sent"
    )
    employee_id = fields.Many2one("hr.employee", readonly=True)
    course_start = fields.Date(related="course_schedule_id.start_date", readonly=True)
    course_end = fields.Date(related="course_schedule_id.end_date", readonly=True)
    state = fields.Selection(related="course_schedule_id.state", readonly=True)
    result = fields.Selection(
        [
            ("passed", "Passed"),
            ("failed", "Failed"),
            ("absent", "Absent"),
            ("pending", "Pending"),
        ],
        string="Result",
        default="pending",
    )
    active = fields.Boolean(default=True, readonly=True)

    def _remove_from_course(self):
        return [(1, self.id, {"active": False})]
