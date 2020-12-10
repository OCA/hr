# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    relative_ids = fields.One2many(
        string="Relatives",
        comodel_name="hr.employee.relative",
        inverse_name="employee_id",
    )

    relatives_count = fields.Integer(compute="_compute_relatives_count")

    @api.depends("relative_ids")
    def _compute_relatives_count(self):
        for record in self:
            record.relatives_count = len(record.relative_ids)

    def action_view_relatives(self):
        self.ensure_one()
        action = self.env.ref("hr_employee_relative.action_employee_relatives").read()[
            0
        ]
        action["domain"] = [("employee_id", "=", self.id)]
        action["context"] = {"default_employee_id": self.id}
        return action
