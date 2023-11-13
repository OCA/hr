# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):

    _inherit = "hr.employee"

    medical_examination_ids = fields.One2many(
        comodel_name="hr.employee.medical.examination",
        inverse_name="employee_id",
    )

    medical_examination_count = fields.Integer(
        compute="_compute_medical_examination_count",
    )

    can_see_examinations_button = fields.Boolean(
        compute="_compute_can_see_examinations_button",
    )

    @api.depends("medical_examination_ids")
    def _compute_medical_examination_count(self):
        for record in self:
            record.medical_examination_count = len(record.medical_examination_ids)

    def _compute_can_see_examinations_button(self):
        for record in self:
            record.can_see_examinations_button = (
                self.env.uid == record.user_id.id
                or self.env.user.has_group("hr.group_hr_manager")
            )
