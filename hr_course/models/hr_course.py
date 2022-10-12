# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


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
