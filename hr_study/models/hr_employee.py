# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    study_id = fields.Many2one(
        comodel_name="hr.study",
        string="Study",
        groups="hr.group_hr_user",
        tracking=True,
    )

    @api.onchange("study_id")
    def _onchange_study_id(self):
        if self.study_id:
            self.study_field = self.study_id.name
