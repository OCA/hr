# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrCourseSchedule(models.Model):
    _name = "hr.course.schedule"
    _description = "Course Schedule"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    name = fields.Char(required=True, tracking=True)
    code = fields.Char(string="Reference", copy=False, index="btree_not_null")
    course_id = fields.Many2one("hr.course", string="Course", required=True)

    start_date = fields.Date(
        tracking=True,
    )
    end_date = fields.Date(
        tracking=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.user.company_id.currency_id,
    )
    cost = fields.Monetary(string="Course Cost", required=True, tracking=True)
    authorized_by = fields.Many2one(
        comodel_name="hr.employee",
        required=True,
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

    comment = fields.Text()
    training_company_id = fields.Many2one("res.partner", string="Training company")
    instructor_ids = fields.Many2many("res.partner", string="Instructor")
    place = fields.Char()

    attendant_ids = fields.Many2many("hr.employee")
    course_attendee_ids = fields.One2many(
        "hr.course.attendee", inverse_name="course_schedule_id"
    )
    note = fields.Text()

    _sql_constraints = [
        (
            "hr_course_schedule_code_uniq",
            "unique (code)",
            "The reference must be unique!",
        ),
    ]

    @api.depends("code", "name")
    def _compute_display_name(self):
        for record in self:
            if record.code and record.name:
                record.display_name = f"[{record.code}] {record.name}"
            elif record.name:
                record.display_name = record.name
            else:
                record.display_name = record.code or ""

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        recs = self.search([("code", operator, name)] + args, limit=limit)
        if not recs.ids:
            return super().name_search(
                name=name, args=args, operator=operator, limit=limit
            )
        return [(r.id, r.display_name) for r in recs]

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("hr.course.schedule") or ""
                )
        return super().create(vals_list)

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
