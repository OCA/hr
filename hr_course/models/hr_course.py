# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrCourse(models.Model):
    _name = "hr.course"
    _description = "Course"
    _inherit = "mail.thread"

    name = fields.Char(string="Name", required=True, tracking=True)
    category_id = fields.Many2one(
        "hr.course.category", string="Category", required=True,
    )

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
    permanence = fields.Boolean(
        string="Has Permanence",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        help="Check if the participants of this course are restricted to"
        " stay in the company for a certain period of time.",
    )
    permanence_time = fields.Char(
        string="Permanence time",
        readonly=True,
        states={"draft": [("readonly", False)]},
        tracking=True,
        help="Amount of time the employee is restricted to stay in the"
        " company by participating to this course.",
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
    attendant_ids = fields.Many2many(
        "hr.employee",
        readonly=True,
        states={"waiting_attendees": [("readonly", False)]},
    )
    course_attendee_ids = fields.One2many(
        "hr.course.attendee",
        inverse_name="course_id",
        readonly=True,
        states={"in_validation": [("readonly", False)]},
    )

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

    @api.onchange("permanence")
    def _onchange_permanence(self):
        self.permanence_time = False

    def _draft2waiting_values(self):
        return {
            "state": "waiting_attendees",
        }

    def _attendee_values(self, attendee):
        return {"employee_id": attendee.id, "course_id": self.id}

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
        return {
            "state": "in_validation",
        }

    def _validation2complete_values(self):
        return {
            "state": "completed",
        }

    def _back2draft_values(self):
        return {
            "state": "draft",
        }

    def _cancel_course_values(self):
        return {
            "state": "cancelled",
        }

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


class HRCourseAttendee(models.Model):
    _name = "hr.course.attendee"
    _description = "Course Attendee"

    course_id = fields.Many2one(
        "hr.course", ondelete="cascade", readonly=True, required=True,
    )
    name = fields.Char(related="course_id.name", readonly=True)
    employee_id = fields.Many2one("hr.employee", readonly=True)
    course_start = fields.Date(related="course_id.start_date", readonly=True)
    course_end = fields.Date(related="course_id.end_date", readonly=True)
    state = fields.Selection(related="course_id.state", readonly=True)
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


class HRCourseCategory(models.Model):
    _name = "hr.course.category"
    _description = "Course Category"
    name = fields.Char(string="Course category", required=True)

    _sql_constraints = [
        ("name_uniq", "unique (name)", "Category already exists !"),
    ]
