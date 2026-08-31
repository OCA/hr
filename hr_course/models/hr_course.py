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
        default="pending",
    )
    active = fields.Boolean(default=True, readonly=True)

    def _remove_from_course(self):
        return [(1, self.id, {"active": False})]


class HrCourse(models.Model):
    _name = "hr.course"
    _description = "Course"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(required=True, tracking=True)
    code = fields.Char(string="Reference", copy=False, index="btree_not_null")
    category_id = fields.Many2one(
        "hr.course.category", string="Category", required=True
    )

    permanence = fields.Boolean(string="Has Permanence", default=False, tracking=True)
    permanence_time = fields.Char(tracking=True)

    content = fields.Html()
    objective = fields.Html()

    evaluation_criteria = fields.Html()

    course_schedule_ids = fields.One2many(
        "hr.course.schedule", inverse_name="course_id"
    )

    _sql_constraints = [
        ("hr_course_code_uniq", "unique (code)", "The reference must be unique!"),
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
                vals["code"] = self.env["ir.sequence"].next_by_code("hr.course") or ""
        return super().create(vals_list)

    @api.onchange("permanence")
    def _onchange_permanence(self):
        self.permanence_time = False


class HRCourseCategory(models.Model):
    _name = "hr.course.category"
    _description = "Course Category"

    name = fields.Char(string="Course category", required=True)

    _sql_constraints = [("name_uniq", "unique (name)", "Category already exists !")]
