# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    document_count = fields.Integer(
        compute="_compute_document_count", string="Document Count",
    )

    def _compute_document_count(self):
        self.documents_count = 0
        attachment_groups = self.env["ir.attachment"].read_group(
            [("res_model", "=", "hr.employee"), ("res_id", "in", self.ids)],
            ["res_id"],
            ["res_id"],
        )
        count_dict = {x["res_id"]: x["res_id_count"] for x in attachment_groups}
        for record in self:
            record.document_count = count_dict.get(record.id, 0)

    def action_get_attachment_tree_view(self):
        action = self.env.ref("base.action_attachment").read()[0]
        action["context"] = {
            "default_res_model": self._name,
            "default_res_id": self.ids[0],
        }
        action["domain"] = str(
            [("res_model", "=", self._name), ("res_id", "in", self.ids)]
        )
        action["search_view_id"] = (
            self.env.ref("hr_employee_document.ir_attachment_view_search").id,
        )
        return action
