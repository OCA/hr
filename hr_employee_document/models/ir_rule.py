# Copyright 2023 Tecnativa - Víctor Martínez
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models, tools
from odoo.osv import expression
from odoo.tools import config


class IrRule(models.Model):
    _inherit = "ir.rule"

    @api.model
    @tools.conditional(
        "xml" not in config["dev_mode"],
        tools.ormcache(
            "self.env.uid",
            "self.env.su",
            "model_name",
            "mode",
            "tuple(self._compute_domain_context_values())",
        ),
    )
    def _compute_domain(self, model_name, mode="read"):
        """We need to add for security purposes an extra domain in the hr.employee
        model to restrict only the user's employees when search employee attachments."""
        res = super()._compute_domain(model_name, mode=mode)
        user = self.env.user
        if (
            model_name == "hr.employee"
            and not self.env.su
            and not user.has_group("hr.group_hr_manager")
            and self.env.context.get("search_attachments_from_hr_employee")
        ):
            extra_domain = [[("id", "in", user.employee_ids.ids)]]
            res = expression.AND(extra_domain + [res])
        return res
