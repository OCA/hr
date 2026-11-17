# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Department(models.Model):
    _inherit = "hr.department"
    _order = "code, name"

    code = fields.Char()

    @api.depends_context("hierarchical_naming")
    @api.depends("code", "name")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for record in self:
            if record.code:
                record.display_name = f"[{record.code}] {record.display_name}"
        return res
