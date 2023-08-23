# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_logged = fields.Boolean(compute="_compute_is_logged", store=False)

    def _compute_is_logged(self):
        self.is_logged = False
        for record in self:
            if self.env.user == record.user_id:
                record.is_logged = True

    def action_get_attachment_tree_view(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("base.action_attachment")
        action["context"] = {
            "default_res_model": "hr.employee",
            "default_res_id": self.env.user.employee_id.id,
            "search_attachments_from_hr_employee": True,
        }
        action["domain"] = [
            ("res_model", "=", "hr.employee"),
            ("res_id", "=", self.env.user.employee_id.id),
        ]
        action["search_view_id"] = (
            self.env.ref("hr_employee_document.ir_attachment_view_search").id,
        )
        return action
