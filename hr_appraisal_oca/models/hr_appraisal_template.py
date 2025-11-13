# Copyright 2025 Fundacion Esment - Estefanía Bauzá
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrAppraisalTemplate(models.Model):
    _name = "hr.appraisal.template"
    _description = "HR Appraisal Templates"
    _rec_name = "description"

    description = fields.Text(required=True)
    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.user.company_id
    )
    appraisal_employee_feedback_template = fields.Html(
        string="Employee Feedback", translate=True
    )
    appraisal_manager_feedback_template = fields.Html(
        string="Manager Feedback", translate=True
    )
    is_default = fields.Boolean(compute="_compute_is_default")

    def _compute_is_default(self):
        default_template_id = int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("hr_appraisal_oca.default_appraisal_template_id", 0)
        )
        for rec in self:
            rec.is_default = rec.id == default_template_id
