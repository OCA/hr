# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class View(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(selection_add=[("circle_pack", "Circle Pack")])

    def _get_view_info(self):
        res = super()._get_view_info()
        res["circle_pack"] = {"icon": "fa fa-share-alt o_hierarchy_icon"}
        return res
