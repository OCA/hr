# Copyright 2025 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import ormcache


class GovernanceRoleType(models.Model):
    _name = "governance.role.type"
    _description = "Governance Role Type"

    name = fields.Char(required=True)
    type = fields.Selection(
        [("template", "Template"), ("structure", "Structure")], required=True
    )
    purpose = fields.Html(
        string="Raison d'être",
    )
    authority = fields.Html(
        string="Domain of authorities",
    )
    expectation = fields.Html(
        string="Expectations",
    )
    color = fields.Integer(default=1)
    is_steering_role = fields.Boolean(default=False)
    source_circle_id = fields.Many2one(
        "governance.circle",
        default=lambda x: x._get_default_source_circle_id(),
        domain="[('is_circle', '=', True)]",
        help="This Role Type are only allowed in the Source Circle and its children",
    )
    enable_edit_circle = fields.Boolean(
        help="If checked, member of this Role type is allowed to modify Circle"
    )
    _sql_constraints = [
        (
            "unique_role_type",
            "unique(name)",
            "This Circle Type already exists",
        ),
    ]

    def _get_default_source_circle_id(self):
        root_circle = self.env.ref(
            "hr_governance.root", raise_if_not_found=False
        ) or self.env["governance.circle"].search([("is_root", "=", True)])
        return root_circle or False

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        self.env.registry.clear_cache()
        return records

    def write(self, vals):
        self._onchange_content_fields(vals)
        return super().write(vals)

    def unlink(self):
        res = super().unlink()
        self.env.registry.clear_cache()
        return res

    ##########################################################################
    # Helpers
    ##########################################################################

    def _onchange_content_fields(self, vals):
        content_fields = ["purpose", "expectation", "authority"]
        changed_content_fields = [field for field in content_fields if field in vals]

        if not changed_content_fields:
            return

        old_values = {}
        for field in changed_content_fields:
            old_values[field] = getattr(self, field) or ""

        for field in changed_content_fields:
            new_value = vals.get(field, "")
            old_value = old_values.get(field, "")
            circles = self.env["governance.circle"].search([("type_id", "=", self.id)])
            for circle in circles:
                circle._update_content(field, new_value, old_value)

    @api.model
    @ormcache()
    def _get_structuring_role_vals(self):
        """Get the default values when creating structure roles"""
        templates = self.env["governance.role.type"].search(
            [("type", "=", "structure")]
        )
        return [
            {"type_id": temp.id, **temp._required_role_fields()} for temp in templates
        ]

    def _required_role_fields(self):
        return {
            "name": self.name,
            "color": self.color,
            "purpose": self.purpose,
            "authority": self.authority,
            "expectation": self.expectation,
        }

    @api.model
    @ormcache()
    def _get_enable_edit_circle_role(self):
        """Get the role that its User edit circles"""
        roles = self.env["governance.role.type"].search(
            [("enable_edit_circle", "=", True)]
        )
        return [{"id": role.id, "name": role.name} for role in roles]
