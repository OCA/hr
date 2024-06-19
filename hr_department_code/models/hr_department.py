# Copyright 2021 Ecosoft Co., Ltd. (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class Department(models.Model):
    _inherit = "hr.department"
    _order = "code, name"

    code = fields.Char()

    @api.depends_context("hierarchical_naming")
    def _compute_display_name(self):
        res = super()._compute_display_name()
        for record in self:
            if record.code:
                record.display_name = f"[{record.code}] {record.display_name}"
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        domain = []
        if name:
            domain = ["|", ("code", operator, name), ("name", operator, name)]
        department = self.search(domain + args, limit=limit)
        return department.name_get()
