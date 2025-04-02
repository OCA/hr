# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class Http(models.AbstractModel):
    _inherit = "ir.http"

    def session_info(self):
        session_info = super().session_info()
        session_info["user_context"][
            "allowed_edit_governance_ids"
        ] = self.env.user.allowed_edit_governance_ids.ids
        return session_info
