# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    document_count = fields.Integer(related="employee_id.document_count")

    def action_get_attachment_tree_view(self):
        return self.employee_id.action_get_attachment_tree_view()
