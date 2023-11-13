# Copyright (C) 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    relative_ids = fields.One2many(
        comodel_name="hr.employee.relative",
        inverse_name="employee_id",
    )

    children = fields.Integer(
        compute="_compute_children",
        store=True,
        readonly=True,
    )

    @api.depends("relative_ids.relation_id")
    def _compute_children(self):
        child_relation_id = self.env.ref("hr_employee_relative.relation_child").id

        for employee in self:
            employee.children = len(
                employee.relative_ids.filtered(
                    lambda r: r.relation_id.id == child_relation_id
                )
            )
