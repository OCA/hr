# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    is_logged = fields.Boolean(compute="_compute_is_logged", store=False)
    document_count = fields.Integer(compute_sudo=True)

    def _compute_is_logged(self):
        self.is_logged = False
        for record in self:
            if self.env.user == record.user_id:
                record.is_logged = True

    def action_get_attachment_tree_view(self):
        return self.employee_id.action_get_attachment_tree_view()
