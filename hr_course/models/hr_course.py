# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HRCourseAttendee(models.Model):
    _name = "hr.course.attendee"
    _description = "Course Attendee"

    course_schedule_id = fields.Many2one(
        "hr.course.schedule", ondelete="cascade", readonly=True, required=True
    )
    name = fields.Char(related="course_schedule_id.name", readonly=True)
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


class HrCourse(models.Model):
    _name = "hr.course"
    _description = "Course"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
    category_id = fields.Many2one(
        "hr.course.category", string="Category", required=True
    )

    permanence = fields.Boolean(
        string="Has Permanence",
        readonly=True,
        default=False,
        tracking=True,
    )
    permanence_time = fields.Char(
        string="Permanence time",
        readonly=True,
        tracking=True,
    )

    content = fields.Html()
    objective = fields.Html()

    evaluation_criteria = fields.Html()

    course_schedule_ids = fields.One2many(
        "hr.course.schedule",
        inverse_name="course_id",
        readonly=True,
    )

    @api.onchange("permanence")
    def _onchange_permanence(self):
        self.permanence_time = False


class HRCourseCategory(models.Model):
    _name = "hr.course.category"
    _description = "Course Category"

    name = fields.Char(string="Course category", required=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Category already exists !")]
