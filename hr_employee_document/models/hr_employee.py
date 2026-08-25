# Copyright 2018 Brainbean Apps (https://brainbeanapps.com)
# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.fields import Domain


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    document_count = fields.Integer(
        compute="_compute_document_count",
    )

    def _compute_document_count(self):
        results = self.env["ir.attachment"]._read_group(
            Domain([("res_model", "=", "hr.employee"), ("res_id", "in", self.ids)]),
            groupby=["res_id"],
            aggregates=["__count"],
        )
        count_dict = {res_id: count for res_id, count in results}
        for record in self:
            record.document_count = count_dict.get(record.id, 0)

    def _check_access(self, operation):
        """Return access to the hr.employee model if we pass a specific context,
        is a trick to list the attachments related to an employee."""
        if (
            not self.env.su
            and not self.env.user.has_group("hr.group_hr_user")
            and operation == "read"
            and self._name == "hr.employee"
        ):
            if (
                self.env.context.get("search_attachments_from_hr_employee")
                or self in self.env.user.employee_ids
            ):
                return None
        return super()._check_access(operation=operation)

    def action_get_attachment_tree_view(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id("base.action_attachment")
        action["context"] = {
            "default_res_model": self._name,
            "default_res_id": self.id,
            "search_attachments_from_hr_employee": True,
            "create": False,
        }
        action["domain"] = Domain(
            [("res_model", "=", self._name), ("res_id", "=", self.id)]
        )
        action["search_view_id"] = (
            self.env.ref("hr_employee_document.ir_attachment_view_search").id,
        )
        return action
