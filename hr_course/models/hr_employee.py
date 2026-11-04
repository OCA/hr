from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    count_courses = fields.Integer(
        "Number of courses", compute="_compute_count_courses"
    )

    courses_ids = fields.One2many(
        "hr.course.attendee",
        "employee_id",
        readonly=True,
    )

    @api.depends("courses_ids")
    def _compute_count_courses(self):
        for r in self:
            r.count_courses = len(r.courses_ids)

    def action_view_course(self):
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "hr_course.action_view_course"
        )
        action["domain"] = [("employee_id", "=", self.id)]
        return action
