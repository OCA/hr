# Copyright 2026 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    def validate_access(self, access_token):
        """It is important to override this method so that employee attachments
        can be previewed
        """
        res = super().validate_access(access_token)
        record_sudo = res.sudo()
        if (
            res
            and record_sudo.res_model == "hr.employee"
            and record_sudo.res_id
            and record_sudo.res_id in self.env.user.employee_ids.ids
        ):
            res = record_sudo
        return res
