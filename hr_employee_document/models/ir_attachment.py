# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def _can_return_content(self, field_name=None, access_token=None):
        if (
            self.res_model == "hr.employee"
            and self.res_id
            and self.res_id in self.env.user.employee_ids.ids
        ):
            return True
        return super()._can_return_content(field_name, access_token)
